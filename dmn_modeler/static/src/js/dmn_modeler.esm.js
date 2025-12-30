/** @odoo-module **/

import {
    Component,
    onMounted,
    onWillUnmount,
    onWillUpdateProps,
    useRef,
    xml,
} from "@odoo/owl";

// IMPORTANT: This component assumes that the dmn-js library (specifically DMNModeler)
// is loaded globally (e.g., via a script tag in the assets or a separate module).
// In a real scenario, you would ensure 'dmn-modeler.development.js' is loaded
// before this file in the 'web.assets_backend' list in __manifest__.py.

export class DMNModeler extends Component {
    static template = xml`
        <div class="o_dmn_modeler_container">
            <div t-ref="canvas" class="canvas"/>
        </div>
    `;

    static props = {
        dmn_xml: {type: String, optional: true},
        readonly: {type: Boolean, optional: true, default: false},
        onChange: {type: Function, optional: true},
        onSVGChange: {type: Function, optional: true},
        onReady: {type: Function, optional: true},
        onValidationChange: {type: Function, optional: true},
    };

    setup() {
        this.canvasRef = useRef("canvas");
        this.dmnModeler = null;
        this._keyboardHandler = null;
        this._wheelHandler = null;

        onMounted(() => {
            this._initDMNModeler();
        });

        onWillUpdateProps((nextProps) => {
            if (nextProps.dmn_xml !== this.props.dmn_xml) {
                this._importXML(nextProps.dmn_xml);
            }
        });

        onWillUnmount(() => {
            // Clean up event listeners
            if (this.canvasRef.el && this._keyboardHandler) {
                this.canvasRef.el.removeEventListener("keydown", this._keyboardHandler);
            }
            if (this.canvasRef.el && this._wheelHandler) {
                this.canvasRef.el.removeEventListener("wheel", this._wheelHandler);
            }

            if (this.dmnModeler) {
                this.dmnModeler.destroy();
            }
        });
    }

    /**
     * Loads the dmn-js library CSS from CDN if not already loaded.
     * The JavaScript library should be loaded via assets in __manifest__.py
     * @private
     */
    async _loadDmnJs() {
        return new Promise((resolve, reject) => {
            // Check if already loaded (from assets or previous load)
            if (window.DmnJS) {
                // Load CSS if not already loaded
                this._loadDmnCss();
                resolve();
                return;
            }

            // Check if already loading
            if (document.querySelector('script[src*="dmn-modeler"]')) {
                const checkLoaded = setInterval(() => {
                    if (window.DmnJS) {
                        clearInterval(checkLoaded);
                        this._loadDmnCss();
                        resolve();
                    }
                }, 100);
                return;
            }

            // If library is not loaded via assets, try loading from CDN as fallback
            console.warn(
                "DMN.js library not found in assets, loading from CDN as fallback"
            );

            // Load CSS files first
            this._loadDmnCss();

            // Load from CDN as fallback
            const script = document.createElement("script");
            script.src =
                "https://unpkg.com/dmn-js@17.5.0/dist/dmn-modeler.development.js";
            script.async = true;
            script.onload = () => {
                console.log("DMN.js modeler loaded successfully from CDN");
                resolve();
            };
            script.onerror = () => {
                console.error("Failed to load DMN.js modeler from CDN");
                reject(new Error("Failed to load DMN.js modeler from CDN"));
            };
            document.head.appendChild(script);
        });
    }

    /**
     * Loads DMN.js CSS files from CDN
     * Order is important: diagram-js.css, dmn-js-shared.css, dmn-js-drd.css, etc.
     * @returns {Promise<void>}
     * @private
     */
    _loadDmnCss() {
        const cssFiles = [
            "https://unpkg.com/dmn-js@17.5.0/dist/assets/diagram-js.css",
            "https://unpkg.com/dmn-js@17.5.0/dist/assets/dmn-js-shared.css",
            "https://unpkg.com/dmn-js@17.5.0/dist/assets/dmn-js-drd.css",
            "https://unpkg.com/dmn-js@17.5.0/dist/assets/dmn-js-decision-table.css",
            "https://unpkg.com/dmn-js@17.5.0/dist/assets/dmn-js-literal-expression.css",
            "https://unpkg.com/dmn-js@17.5.0/dist/assets/dmn-font/css/dmn.css",
        ];

        // Load CSS files sequentially to ensure proper order
        return cssFiles.reduce((promise, href) => {
            return promise.then(() => {
                return new Promise((resolve) => {
                    // Check if already loaded
                    const existingLink = document.querySelector(`link[href="${href}"]`);
                    if (existingLink) {
                        resolve();
                        return;
                    }

                    const link = document.createElement("link");
                    link.rel = "stylesheet";
                    link.type = "text/css";
                    link.href = href;

                    // Wait for CSS to load
                    link.onload = () => {
                        // Small delay to ensure styles are applied
                        setTimeout(resolve, 50);
                    };
                    link.onerror = () => {
                        console.warn(`Failed to load CSS: ${href}`);
                        resolve();
                    };

                    document.head.appendChild(link);
                });
            });
        }, Promise.resolve());
    }

    /**
     * Initializes the dmn-js modeler.
     * @private
     */
    async _initDMNModeler() {
        try {
            // Ensure CSS is loaded first (critical for proper rendering)
            await this._loadDmnCss();

            // Load dmn-js library if not already loaded
            await this._loadDmnJs();

            // Check if dmn-js library is available globally
            if (typeof window.DmnJS === "undefined") {
                console.error("DMN library not found. Please ensure dmn-js is loaded.");
                return;
            }

            // Use DmnJS from window (dmn-js library)
            // Note: keyboard.bindTo was removed in newer versions of dmn-js
            this.dmnModeler = new window.DmnJS({
                container: this.canvasRef.el,
            });

            // Setup event listeners first
            this.dmnModeler.on("commandStack.changed", () => {
                this._saveDiagram();
                this._updateValidationStats();
            });

            // Listen to diagram changes for validation
            // This event is fired when the modeler is ready and has imported XML
            this.dmnModeler.on("import.done", () => {
                this._updateValidationStats();
            });

            // Setup keyboard shortcuts for undo/redo
            if (!this.props.readonly) {
                this._setupKeyboardShortcuts();
            }

            // Setup mouse wheel zoom
            this._setupMouseWheelZoom();

            // Setup minimap if available
            this._setupMinimap();

            // Expose API methods to parent component
            if (this.props.onReady) {
                this.props.onReady({
                    exportDiagram: () => this.exportDiagram(),
                    exportSVG: () => this.exportSVG(),
                    exportPNG: () => this.exportPNG(),
                    exportPDF: () => this.exportPDF(),
                    importDiagram: (xmlContent) => this.importDiagram(xmlContent),
                    zoomIn: () => this.zoomIn(),
                    zoomOut: () => this.zoomOut(),
                    zoomFit: () => this.zoomFit(),
                    zoomReset: () => this.zoomReset(),
                    undo: () => this.undo(),
                    redo: () => this.redo(),
                    canUndo: () => this.canUndo(),
                    canRedo: () => this.canRedo(),
                    getValidationStats: () => this.getValidationStats(),
                });
            }

            // Import XML - this will initialize the modeler
            // The import.done event will be fired when ready
            await this._importXML(this.props.dmn_xml || "");
        } catch (err) {
            console.error("Error initializing DMN modeler:", err);
        }
    }

    /**
     * Imports DMN XML into the modeler.
     * @param {String} xmlString The DMN XML string.
     * @private
     */
    async _importXML(xmlString) {
        if (!this.dmnModeler) {
            return;
        }
        try {
            await this.dmnModeler.importXML(xmlString);
            // Check if get method is available before using it
            if (typeof this.dmnModeler.get === "function") {
                const canvas = this.dmnModeler.get("canvas");
                if (canvas && typeof canvas.zoom === "function") {
                    canvas.zoom("fit-viewport");
                }
            }
        } catch (err) {
            console.error("could not import DMN diagram", err);
        }
    }

    /**
     * Saves the current diagram as XML and emits the change.
     * Also generates SVG for preview.
     * @private
     */
    async _saveDiagram() {
        if (!this.dmnModeler || this.props.readonly) {
            return;
        }
        try {
            // Check if saveXML method is available
            if (typeof this.dmnModeler.saveXML !== "function") {
                console.warn("DMN modeler saveXML method not available");
                return;
            }

            const {xml: xmlContent} = await this.dmnModeler.saveXML({format: true});
            if (this.props.onChange) {
                this.props.onChange(xmlContent);
            }

            // Also generate SVG for preview (only if saveSVG is available)
            if (typeof this.dmnModeler.saveSVG === "function") {
                try {
                    const {svg} = await this.dmnModeler.saveSVG();
                    if (this.props.onSVGChange) {
                        this.props.onSVGChange(svg);
                    }
                } catch (svgErr) {
                    // SVG generation is optional, don't fail if it errors
                    console.warn("Could not generate SVG preview:", svgErr);
                }
            }
        } catch (err) {
            console.error("could not save DMN diagram", err);
        }
    }

    /**
     * Exports the current diagram as DMN XML file.
     * @public
     * @returns {Promise<String>} The DMN XML string.
     */
    async exportDiagram() {
        if (!this.dmnModeler) {
            console.error("DMN modeler not initialized");
            return null;
        }
        if (typeof this.dmnModeler.saveXML !== "function") {
            console.error("DMN modeler saveXML method not available");
            return null;
        }
        try {
            const {xml: xmlContent} = await this.dmnModeler.saveXML({format: true});
            return xmlContent;
        } catch (err) {
            console.error("could not export DMN diagram", err);
            return null;
        }
    }

    /**
     * Imports a DMN XML diagram.
     * @public
     * @param {String} xmlContent The DMN XML string to import.
     * @returns {Promise<void>}
     */
    async importDiagram(xmlContent) {
        if (!this.dmnModeler) {
            console.error("DMN modeler not initialized");
            return;
        }
        try {
            await this._importXML(xmlContent);
            // Trigger save to update the field
            await this._saveDiagram();
        } catch (err) {
            console.error("could not import DMN diagram", err);
            throw err;
        }
    }

    /**
     * Exports the current diagram as SVG.
     * @public
     * @returns {Promise<String>} The SVG string.
     */
    async exportSVG() {
        if (!this.dmnModeler) {
            console.error("DMN modeler not initialized");
            return null;
        }
        if (typeof this.dmnModeler.saveSVG !== "function") {
            console.error("DMN modeler saveSVG method not available");
            return null;
        }
        try {
            // Use saveSVG to export DMN diagram as SVG
            // DMN uses DMNDI (DMN Diagram Interchange) by default
            const {svg} = await this.dmnModeler.saveSVG();

            // Ensure SVG has proper dimensions and viewBox
            if (svg) {
                return this._enhanceSVG(svg);
            }
            return svg;
        } catch (err) {
            console.error("could not export SVG", err);
            return null;
        }
    }

    /**
     * Enhances SVG to ensure all elements are visible.
     * @param {String} svg The SVG string.
     * @returns {String} Enhanced SVG string.
     * @private
     */
    _enhanceSVG(svg) {
        try {
            const parser = new DOMParser();
            const svgDoc = parser.parseFromString(svg, "image/svg+xml");
            const svgElement = svgDoc.documentElement;

            // Ensure all paths, lines, and connections have proper stroke properties
            const connections = svgDoc.querySelectorAll(
                'path.djs-connection, path[class*="connection"], line, polyline'
            );
            connections.forEach((conn) => {
                // Get computed styles from the actual rendered element if possible
                const computedStyle = window.getComputedStyle(conn) || {};
                const stroke =
                    conn.getAttribute("stroke") || computedStyle.stroke || "#000000";
                const strokeWidth =
                    conn.getAttribute("stroke-width") ||
                    computedStyle.strokeWidth ||
                    "2";

                conn.setAttribute("stroke", stroke);
                conn.setAttribute("stroke-width", strokeWidth);
                if (
                    !conn.getAttribute("fill") ||
                    conn.getAttribute("fill") === "none"
                ) {
                    conn.setAttribute("fill", "none");
                }
            });

            // Ensure all paths (including connections) have stroke
            const paths = svgDoc.querySelectorAll("path");
            paths.forEach((path) => {
                // Skip if already processed as connection
                if (
                    path.classList.contains("djs-connection") ||
                    path.getAttribute("class")?.includes("connection")
                ) {
                    return;
                }

                if (!path.getAttribute("stroke")) {
                    path.setAttribute("stroke", "#000000");
                }
                if (!path.getAttribute("stroke-width")) {
                    path.setAttribute("stroke-width", "2");
                }
            });

            // Ensure viewBox exists
            if (!svgElement.getAttribute("viewBox")) {
                const width = parseFloat(svgElement.getAttribute("width")) || 1200;
                const height = parseFloat(svgElement.getAttribute("height")) || 800;
                svgElement.setAttribute("viewBox", `0 0 ${width} ${height}`);
            }

            // Add style element to ensure connections are visible
            let styleElement = svgDoc.querySelector("style");
            if (!styleElement) {
                styleElement = svgDoc.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "style"
                );
                svgElement.insertBefore(styleElement, svgElement.firstChild);
            }

            // Add CSS rules for connections
            const styleText = styleElement.textContent || "";
            if (!styleText.includes(".djs-connection")) {
                const additionalStyles = `
                    .djs-connection { stroke: #000000 !important; stroke-width: 2px !important; fill: none !important; }
                    path.djs-connection { stroke: #000000 !important; stroke-width: 2px !important; fill: none !important; }
                    .djs-edge { stroke: #000000 !important; stroke-width: 2px !important; }
                `;
                styleElement.textContent = styleText + additionalStyles;
            }

            const serializer = new XMLSerializer();
            return serializer.serializeToString(svgElement);
        } catch (err) {
            console.warn("Failed to enhance SVG:", err);
            return svg;
        }
    }

    /**
     * Zooms in the canvas.
     * @public
     */
    zoomIn() {
        if (!this.dmnModeler || typeof this.dmnModeler.get !== "function") {
            return;
        }
        const canvas = this.dmnModeler.get("canvas");
        if (canvas && typeof canvas.zoom === "function") {
            const currentZoom = canvas.zoom();
            canvas.zoom(Math.min(currentZoom * 1.2, 3));
        }
    }

    /**
     * Zooms out the canvas.
     * @public
     */
    zoomOut() {
        if (!this.dmnModeler || typeof this.dmnModeler.get !== "function") {
            return;
        }
        const canvas = this.dmnModeler.get("canvas");
        if (canvas && typeof canvas.zoom === "function") {
            const currentZoom = canvas.zoom();
            canvas.zoom(Math.max(currentZoom / 1.2, 0.2));
        }
    }

    /**
     * Fits the diagram to viewport.
     * @public
     */
    zoomFit() {
        if (!this.dmnModeler || typeof this.dmnModeler.get !== "function") {
            return;
        }
        const canvas = this.dmnModeler.get("canvas");
        if (canvas && typeof canvas.zoom === "function") {
            canvas.zoom("fit-viewport");
        }
    }

    /**
     * Resets zoom to 1.0.
     * @public
     */
    zoomReset() {
        if (!this.dmnModeler || typeof this.dmnModeler.get !== "function") {
            return;
        }
        const canvas = this.dmnModeler.get("canvas");
        if (canvas && typeof canvas.zoom === "function") {
            canvas.zoom(1.0);
        }
    }

    /**
     * Undoes the last action.
     * @public
     */
    undo() {
        if (!this.dmnModeler || this.props.readonly || typeof this.dmnModeler.get !== "function") {
            return;
        }
        const commandStack = this.dmnModeler.get("commandStack");
        if (commandStack && typeof commandStack.canUndo === "function" && commandStack.canUndo()) {
            commandStack.undo();
        }
    }

    /**
     * Redoes the last undone action.
     * @public
     */
    redo() {
        if (!this.dmnModeler || this.props.readonly || typeof this.dmnModeler.get !== "function") {
            return;
        }
        const commandStack = this.dmnModeler.get("commandStack");
        if (commandStack && typeof commandStack.canRedo === "function" && commandStack.canRedo()) {
            commandStack.redo();
        }
    }

    /**
     * Checks if undo is available.
     * @public
     * @returns {Boolean}
     */
    canUndo() {
        if (!this.dmnModeler || this.props.readonly || typeof this.dmnModeler.get !== "function") {
            return false;
        }
        const commandStack = this.dmnModeler.get("commandStack");
        return commandStack && typeof commandStack.canUndo === "function" && commandStack.canUndo();
    }

    /**
     * Checks if redo is available.
     * @public
     * @returns {Boolean}
     */
    canRedo() {
        if (!this.dmnModeler || this.props.readonly || typeof this.dmnModeler.get !== "function") {
            return false;
        }
        const commandStack = this.dmnModeler.get("commandStack");
        return commandStack && typeof commandStack.canRedo === "function" && commandStack.canRedo();
    }

    /**
     * Sets up keyboard shortcuts for undo/redo.
     * @private
     */
    _setupKeyboardShortcuts() {
        if (!this.dmnModeler) {
            return;
        }

        this._keyboardHandler = (ev) => {
            // Check if Ctrl/Cmd is pressed
            if (!ev.ctrlKey && !ev.metaKey) {
                return;
            }

            // Check if we're not typing in an input field
            if (ev.target.tagName === "INPUT" || ev.target.tagName === "TEXTAREA") {
                return;
            }

            // Undo: Ctrl+Z or Cmd+Z
            if (ev.key === "z" && !ev.shiftKey) {
                ev.preventDefault();
                this.undo();
            }

            // Redo: Ctrl+Y or Ctrl+Shift+Z or Cmd+Shift+Z
            if (ev.key === "y" || (ev.key === "z" && ev.shiftKey)) {
                ev.preventDefault();
                this.redo();
            }
        };

        // Add event listener to canvas container
        if (this.canvasRef.el) {
            this.canvasRef.el.addEventListener("keydown", this._keyboardHandler);
            // Make canvas focusable for keyboard events
            this.canvasRef.el.setAttribute("tabindex", "0");
        }
    }

    /**
     * Sets up mouse wheel zoom.
     * @private
     */
    _setupMouseWheelZoom() {
        if (!this.dmnModeler || this.props.readonly || typeof this.dmnModeler.get !== "function") {
            return;
        }

        this._wheelHandler = (ev) => {
            // Check if Ctrl key is pressed (standard zoom behavior)
            if (!ev.ctrlKey && !ev.metaKey) {
                return;
            }

            ev.preventDefault();

            if (typeof this.dmnModeler.get !== "function") {
                return;
            }

            const canvas = this.dmnModeler.get("canvas");
            if (!canvas || typeof canvas.zoom !== "function") {
                return;
            }

            const currentZoom = canvas.zoom();
            const delta = ev.deltaY > 0 ? 0.9 : 1.1;
            const newZoom = Math.max(0.2, Math.min(3, currentZoom * delta));

            // Get mouse position relative to canvas
            const rect = this.canvasRef.el.getBoundingClientRect();
            const center = {
                x: ev.clientX - rect.left,
                y: ev.clientY - rect.top,
            };

            canvas.zoom(newZoom, center);
        };

        // Add event listener to canvas container
        if (this.canvasRef.el) {
            this.canvasRef.el.addEventListener("wheel", this._wheelHandler, {
                passive: false,
            });
        }
    }

    /**
     * Sets up minimap if available.
     * @private
     */
    _setupMinimap() {
        if (!this.dmnModeler || typeof this.dmnModeler.get !== "function") {
            return;
        }

        // Check if minimap module is available
        try {
            const minimap = this.dmnModeler.get("minimap", false);
            if (minimap) {
                // Minimap is already integrated in dmn-js
                console.log("Minimap available");
            }
        } catch (err) {
            // Minimap module not available, that's okay
            console.debug("Minimap not available");
        }
    }

    /**
     * Gets validation statistics for the current diagram.
     * @public
     * @returns {Object} Validation statistics.
     */
    getValidationStats() {
        if (!this.dmnModeler) {
            return null;
        }

        // Check if get method is available
        if (typeof this.dmnModeler.get !== "function") {
            return null;
        }

        try {
            const elementRegistry = this.dmnModeler.get("elementRegistry");
            if (!elementRegistry) {
                return null;
            }
            const elements = elementRegistry.getAll();

            const stats = {
                totalElements: elements.length,
                decisions: 0,
                decisionTables: 0,
                inputs: 0,
                outputs: 0,
                rules: 0,
                literalExpressions: 0,
            };

            elements.forEach((element) => {
                const type = element.type || "";
                if (type.includes("Decision")) {
                    stats.decisions++;
                } else if (type.includes("DecisionTable")) {
                    stats.decisionTables++;
                } else if (type.includes("Input")) {
                    stats.inputs++;
                } else if (type.includes("Output")) {
                    stats.outputs++;
                } else if (type.includes("Rule")) {
                    stats.rules++;
                } else if (type.includes("LiteralExpression")) {
                    stats.literalExpressions++;
                }
            });

            return stats;
        } catch (err) {
            console.error("Error getting validation stats:", err);
            return null;
        }
    }

    /**
     * Updates validation statistics and notifies parent.
     * @private
     */
    _updateValidationStats() {
        const stats = this.getValidationStats();
        if (stats && this.props.onValidationChange) {
            this.props.onValidationChange(stats);
        }
    }

    /**
     * Exports the current diagram as PNG.
     * @public
     * @returns {Promise<Blob>} The PNG blob.
     */
    async exportPNG() {
        if (!this.dmnModeler) {
            console.error("DMN modeler not initialized");
            return null;
        }
        if (typeof this.dmnModeler.saveSVG !== "function") {
            console.error("DMN modeler saveSVG method not available");
            return null;
        }
        try {
            // Export DMN diagram as SVG (DMNDI is included by default)
            const {svg} = await this.dmnModeler.saveSVG();
            // Enhance SVG to ensure all connections are visible
            const enhancedSvg = this._enhanceSVG(svg);
            return await this._svgToPNG(enhancedSvg);
        } catch (err) {
            console.error("could not export PNG", err);
            return null;
        }
    }

    /**
     * Exports the current diagram as PDF.
     * @public
     * @returns {Promise<Blob>} The PDF blob.
     */
    async exportPDF() {
        if (!this.dmnModeler) {
            console.error("DMN modeler not initialized");
            return null;
        }
        if (typeof this.dmnModeler.saveSVG !== "function") {
            console.error("DMN modeler saveSVG method not available");
            return null;
        }
        try {
            // Export DMN diagram as SVG (DMNDI is included by default)
            const {svg} = await this.dmnModeler.saveSVG();
            // Enhance SVG to ensure all connections are visible
            const enhancedSvg = this._enhanceSVG(svg);
            return await this._svgToPDF(enhancedSvg);
        } catch (err) {
            console.error("could not export PDF", err);
            return null;
        }
    }

    /**
     * Converts SVG to PNG.
     * @param {String} svg The SVG string.
     * @returns {Promise<Blob>} The PNG blob.
     * @private
     */
    async _svgToPNG(svg) {
        return new Promise((resolve, reject) => {
            try {
                // Parse SVG to get dimensions
                const parser = new DOMParser();
                const svgDoc = parser.parseFromString(svg, "image/svg+xml");
                const svgElement = svgDoc.documentElement;

                // Get viewBox or width/height from SVG
                let width = 0;
                let height = 0;

                const viewBox = svgElement.getAttribute("viewBox");
                if (viewBox) {
                    const parts = viewBox.split(/\s+|,/);
                    width = parseFloat(parts[2]) || 1200;
                    height = parseFloat(parts[3]) || 800;
                } else {
                    width = parseFloat(svgElement.getAttribute("width")) || 1200;
                    height = parseFloat(svgElement.getAttribute("height")) || 800;
                }

                // Ensure minimum dimensions
                width = Math.max(width, 1200);
                height = Math.max(height, 800);

                // Set explicit width and height on SVG for rendering
                svgElement.setAttribute("width", width);
                svgElement.setAttribute("height", height);
                svgElement.setAttribute("xmlns", "http://www.w3.org/2000/svg");

                // Create serialized SVG with explicit dimensions
                const serializer = new XMLSerializer();
                const svgString = serializer.serializeToString(svgElement);

                // Create image from SVG
                const img = new Image();
                const svgBlob = new Blob([svgString], {
                    type: "image/svg+xml;charset=utf-8",
                });
                const url = URL.createObjectURL(svgBlob);

                img.onload = () => {
                    // Use higher resolution for better quality
                    const scale = 2;
                    const canvas = document.createElement("canvas");
                    canvas.width = width * scale;
                    canvas.height = height * scale;
                    const ctx = canvas.getContext("2d");

                    // Enable high-quality rendering
                    ctx.imageSmoothingEnabled = true;
                    ctx.imageSmoothingQuality = "high";

                    // Fill white background
                    ctx.fillStyle = "#ffffff";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // Scale context for high DPI
                    ctx.scale(scale, scale);

                    // Draw the image
                    ctx.drawImage(img, 0, 0, width, height);

                    canvas.toBlob(
                        (blob) => {
                            URL.revokeObjectURL(url);
                            if (blob) {
                                resolve(blob);
                            } else {
                                reject(new Error("Failed to convert SVG to PNG"));
                            }
                        },
                        "image/png",
                        1.0
                    );
                };

                img.onerror = (err) => {
                    URL.revokeObjectURL(url);
                    console.error("SVG image load error:", err);
                    reject(new Error("Failed to load SVG image"));
                };

                img.src = url;
            } catch (err) {
                console.error("SVG to PNG conversion error:", err);
                reject(err);
            }
        });
    }

    /**
     * Converts SVG to PDF using jsPDF library.
     * @param {String} svg The SVG string.
     * @returns {Promise<Blob>} The PDF blob.
     * @private
     */
    async _svgToPDF(svg) {
        // Load jsPDF library if not already loaded
        await this._loadJsPDF();

        // Convert SVG to PNG first
        const pngBlob = await this._svgToPNG(svg);
        const imgDataUrl = await this._blobToDataURL(pngBlob);

        // Create PDF using jsPDF
        if (typeof window.jspdf !== "undefined") {
            const {jsPDF} = window.jspdf;

            // Get image dimensions first
            const img = new Image();
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
                img.src = imgDataUrl;
            });

            // Determine orientation based on image dimensions
            const isLandscape = img.width > img.height;
            const pdf = new jsPDF({
                orientation: isLandscape ? "landscape" : "portrait",
                unit: "mm",
                format: "a4",
            });

            // Calculate dimensions to fit page
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = pdf.internal.pageSize.getHeight();

            // Convert image pixels to mm (assuming 96 DPI)
            const mmPerPixel = 25.4 / 96;
            const imgWidthMM = img.width * mmPerPixel;
            const imgHeightMM = img.height * mmPerPixel;

            // Calculate scaling to fit page
            const ratio = Math.min(pdfWidth / imgWidthMM, pdfHeight / imgHeightMM);
            const scaledWidth = imgWidthMM * ratio;
            const scaledHeight = imgHeightMM * ratio;

            // Center the image
            const x = (pdfWidth - scaledWidth) / 2;
            const y = (pdfHeight - scaledHeight) / 2;

            pdf.addImage(imgDataUrl, "PNG", x, y, scaledWidth, scaledHeight);
            return pdf.output("blob");
        }
        // Fallback: return PNG if jsPDF is not available
        console.warn("jsPDF not available, returning PNG instead");
        return pngBlob;
    }

    /**
     * Loads jsPDF library dynamically.
     * @returns {Promise<void>}
     * @private
     */
    async _loadJsPDF() {
        if (typeof window.jspdf !== "undefined") {
            return;
        }

        return new Promise((resolve, reject) => {
            // Check if script already exists
            const existingScript = document.querySelector('script[src*="jspdf"]');
            if (existingScript) {
                existingScript.addEventListener("load", resolve);
                existingScript.addEventListener("error", reject);
                return;
            }

            // Load jsPDF from CDN
            const script = document.createElement("script");
            script.src =
                "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
            script.async = true;
            script.onload = () => {
                if (typeof window.jspdf === "undefined") {
                    reject(new Error("jsPDF failed to load"));
                } else {
                    resolve();
                }
            };
            script.onerror = () => reject(new Error("Failed to load jsPDF library"));
            document.head.appendChild(script);
        });
    }

    /**
     * Converts a blob to data URL.
     * @param {Blob} blob The blob to convert.
     * @returns {Promise<String>} The data URL.
     * @private
     */
    _blobToDataURL(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
}
