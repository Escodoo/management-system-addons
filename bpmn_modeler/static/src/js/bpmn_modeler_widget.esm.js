/** @odoo-module **/

import {Component, onMounted, onWillUnmount, useRef, useState, xml} from "@odoo/owl";
import {registry} from "@web/core/registry";

import {useService} from "@web/core/utils/hooks";
// eslint-disable-next-line sort-imports
import {standardFieldProps} from "@web/views/fields/standard_field_props";
// eslint-disable-next-line sort-imports
import {BPMNModeler} from "./bpmn_modeler.esm";

export class BpmnModelerWidget extends Component {
    static template = xml`
        <div class="o_field_bpmn_modeler" t-ref="container">
            <div class="o_bpmn_drop_zone" t-if="state.showDropZone">
                <div class="o_bpmn_drop_overlay">
                    <i class="fa fa-cloud-upload fa-3x"/>
                    <p>Drop BPMN file here to import</p>
                </div>
            </div>
            <div class="o_bpmn_toolbar">
                <div class="o_bpmn_toolbar_group">
                    <button
                        class="btn btn-secondary"
                        t-on-click="onImportClick"
                        t-att-disabled="isImportDisabled"
                        title="Import BPMN file"
                    >
                        <i class="fa fa-upload"/> Import
                    </button>
                    <button class="btn btn-primary" t-on-click="onExportClick" title="Export as BPMN XML">
                        <i class="fa fa-download"/> Export XML
                    </button>
                    <button class="btn btn-info" t-on-click="onExportSVGClick" title="Export as SVG">
                        <i class="fa fa-image"/> Export SVG
                    </button>
                    <button class="btn btn-success" t-on-click="onExportPNGClick" title="Export as PNG">
                        <i class="fa fa-file-image-o"/> Export PNG
                    </button>
                    <button class="btn btn-warning" t-on-click="onExportPDFClick" title="Export as PDF">
                        <i class="fa fa-file-pdf-o"/> Export PDF
                    </button>
                </div>
                <div class="o_bpmn_toolbar_group">
                    <button class="btn btn-sm btn-secondary" t-on-click="onZoomOutClick" title="Zoom Out">
                        <i class="fa fa-search-minus"/>
                    </button>
                    <button class="btn btn-sm btn-secondary" t-on-click="onZoomFitClick" title="Fit to Viewport">
                        <i class="fa fa-arrows-alt"/>
                    </button>
                    <button class="btn btn-sm btn-secondary" t-on-click="onZoomResetClick" title="Reset Zoom">
                        <i class="fa fa-search"/>
                    </button>
                    <button class="btn btn-sm btn-secondary" t-on-click="onZoomInClick" title="Zoom In">
                        <i class="fa fa-search-plus"/>
                    </button>
                </div>
                <input
                    type="file"
                    accept=".bpmn,.xml"
                    t-ref="fileInput"
                    style="display: none;"
                    t-on-change="onFileSelected"
                />
            </div>
            <div class="o_bpmn_validation_stats" t-if="state.validationStats">
                <small>
                    <i class="fa fa-info-circle"/>
                    Elements: <t t-esc="state.validationStats.totalElements"/> |
                    Start: <t t-esc="state.validationStats.startEvents"/> |
                    End: <t t-esc="state.validationStats.endEvents"/> |
                    Tasks: <t t-esc="state.validationStats.tasks"/> |
                    Gateways: <t t-esc="state.validationStats.gateways"/>
                </small>
            </div>
            <BPMNModeler
                bpmn_xml="props.value || ''"
                readonly="props.readonly"
                onChange="(xmlContent) => this._onChange(xmlContent)"
                onSVGChange="(svg) => this._onSVGChange(svg)"
                onReady="(api) => this._onBpmnReady(api)"
                onValidationChange="(stats) => this._onValidationChange(stats)"
            />
        </div>
    `;

    static components = {
        BPMNModeler,
    };

    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.bpmnApi = null;
        this.fileInputRef = useRef("fileInput");
        this.containerRef = useRef("container");
        this.notification = useService("notification");
        this.state = useState({
            showDropZone: false,
            validationStats: null,
        });

        onMounted(() => {
            this._setupDragAndDrop();
        });

        onWillUnmount(() => {
            this._cleanupDragAndDrop();
        });
    }

    /**
     * Checks if the diagram is in draft state.
     * @returns {Boolean} True if the diagram state is "draft", false otherwise.
     */
    get isDraft() {
        if (!this.props.record || !this.props.record.data) {
            return false;
        }
        return this.props.record.data.state === "draft";
    }

    /**
     * Checks if the import button should be disabled.
     * @returns {Boolean} True if import should be disabled, false otherwise.
     */
    get isImportDisabled() {
        return !this.isDraft;
    }

    /**
     * Handles the change event from the OWL BPMNModeler component.
     * @param {String} xmlContent The updated BPMN XML string.
     * @private
     */
    _onChange(xmlContent) {
        if (!this.props.readonly) {
            this.props.update(xmlContent);
        }
    }

    /**
     * Handles the SVG change event from the OWL BPMNModeler component.
     * @param {String} svg The updated SVG string.
     * @private
     */
    async _onSVGChange(svg) {
        // SVG is saved automatically when exporting, but we can also update it here
        // Note: This requires the record to have svg_content field
        if (!this.props.readonly && this.props.record) {
            try {
                // Update the record with SVG content
                const updates = {svg_content: svg};
                await this.props.record.update(updates);
            } catch (err) {
                // Field might not exist, which is okay
                console.debug("SVG field update skipped:", err);
            }
        }
    }

    /**
     * Called when BPMN modeler is ready and exposes its API.
     * @param {Object} api The API object with export method.
     * @private
     */
    _onBpmnReady(api) {
        this.bpmnApi = api;
        // Update validation stats when modeler is ready
        this._updateValidationStats();
    }

    /**
     * Sets up drag and drop functionality.
     * @private
     */
    _setupDragAndDrop() {
        if (!this.containerRef.el || !this.isDraft) {
            return;
        }

        const container = this.containerRef.el;

        const handleDragEnter = (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (
                this.isDraft &&
                e.dataTransfer.items &&
                e.dataTransfer.items.length > 0
            ) {
                this.state.showDropZone = true;
            }
        };

        const handleDragOver = (e) => {
            e.preventDefault();
            e.stopPropagation();
        };

        const handleDragLeave = (e) => {
            e.preventDefault();
            e.stopPropagation();
            // Only hide if we're leaving the container
            if (!this.containerRef.el.contains(e.relatedTarget)) {
                this.state.showDropZone = false;
            }
        };

        const handleDrop = async (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.state.showDropZone = false;

            if (!this.isDraft) {
                this.notification.add(
                    this.env._t(
                        "Import is only allowed when the diagram is in draft state."
                    ),
                    {type: "warning"}
                );
                return;
            }

            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                const file = files[0];
                if (this._validateFile(file)) {
                    await this._handleFileImport(file);
                } else {
                    this.notification.add(
                        this.env._t("Invalid file. Please drop a .bpmn or .xml file."),
                        {type: "danger"}
                    );
                }
            }
        };

        container.addEventListener("dragenter", handleDragEnter);
        container.addEventListener("dragover", handleDragOver);
        container.addEventListener("dragleave", handleDragLeave);
        container.addEventListener("drop", handleDrop);

        // Store handlers for cleanup
        this._dragHandlers = {
            dragenter: handleDragEnter,
            dragover: handleDragOver,
            dragleave: handleDragLeave,
            drop: handleDrop,
        };
    }

    /**
     * Cleans up drag and drop event listeners.
     * @private
     */
    _cleanupDragAndDrop() {
        if (!this.containerRef.el || !this._dragHandlers) {
            return;
        }

        const container = this.containerRef.el;
        Object.keys(this._dragHandlers).forEach((event) => {
            container.removeEventListener(event, this._dragHandlers[event]);
        });
        this._dragHandlers = null;
    }

    /**
     * Validates if a file is a valid BPMN file.
     * @param {File} file The file to validate.
     * @returns {Boolean} True if valid, false otherwise.
     * @private
     */
    _validateFile(file) {
        if (!file) {
            return false;
        }

        const validExtensions = [".bpmn", ".xml"];
        const fileName = file.name.toLowerCase();
        const hasValidExtension = validExtensions.some((ext) => fileName.endsWith(ext));

        const validTypes = ["application/xml", "text/xml", "application/bpmn20-xml"];
        const hasValidType = validTypes.includes(file.type) || file.type === "";

        return hasValidExtension || hasValidType;
    }

    /**
     * Handles file import from drag and drop or file input.
     * @param {File} file The file to import.
     * @private
     */
    async _handleFileImport(file) {
        if (!this.isDraft) {
            this.notification.add(
                this.env._t(
                    "Import is only allowed when the diagram is in draft state."
                ),
                {type: "warning"}
            );
            return;
        }
        try {
            const xmlContent = await this._readFileAsText(file);
            if (xmlContent && this.bpmnApi && this.bpmnApi.importDiagram) {
                await this.bpmnApi.importDiagram(xmlContent);
                // Update the field value
                if (!this.props.readonly) {
                    this.props.update(xmlContent);
                }
                // Update validation stats
                this._updateValidationStats();
            }
        } catch (err) {
            console.error("Error importing BPMN file:", err);
            this.notification.add(
                this.env._t(
                    "Error importing BPMN file. Please make sure it is a valid BPMN XML file."
                ),
                {type: "danger"}
            );
        }
    }

    /**
     * Handles the import click event.
     * @private
     */
    onImportClick() {
        if (!this.isDraft) {
            this.notification.add(
                this.env._t(
                    "Import is only allowed when the diagram is in draft state."
                ),
                {type: "warning"}
            );
            return;
        }
        if (this.fileInputRef.el) {
            this.fileInputRef.el.click();
        }
    }

    /**
     * Handles the file selection event.
     * @param {Event} ev The file input change event.
     * @private
     */
    async onFileSelected(ev) {
        const file = ev.target.files?.[0];
        if (!file) {
            return;
        }

        if (!this._validateFile(file)) {
            this.notification.add("Invalid file. Please select a .bpmn or .xml file.", {
                type: "danger",
            });
            if (this.fileInputRef.el) {
                this.fileInputRef.el.value = "";
            }
            return;
        }

        await this._handleFileImport(file);

        // Reset file input
        if (this.fileInputRef.el) {
            this.fileInputRef.el.value = "";
        }
    }

    /**
     * Reads a file as text.
     * @param {File} file The file to read.
     * @returns {Promise<String>} The file content as text.
     * @private
     */
    _readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    }

    /**
     * Handles the export click event.
     * @private
     */
    async onExportClick() {
        if (this.bpmnApi && this.bpmnApi.exportDiagram) {
            const xmlContent = await this.bpmnApi.exportDiagram();
            if (xmlContent) {
                this._downloadBpmnFile(xmlContent);
            }
        } else {
            console.error("BPMN modeler not ready yet");
        }
    }

    /**
     * Handles the export SVG click event.
     * @private
     */
    async onExportSVGClick() {
        if (this.bpmnApi && this.bpmnApi.exportSVG) {
            const svg = await this.bpmnApi.exportSVG();
            if (svg) {
                this._downloadSVGFile(svg);
                // Also update the svg_content field if available
                if (!this.props.readonly && this.props.record) {
                    try {
                        await this.props.record.update({svg_content: svg});
                    } catch (err) {
                        console.debug("Could not update SVG field:", err);
                    }
                }
            }
        } else {
            console.error("BPMN modeler not ready yet");
        }
    }

    /**
     * Handles the export PNG click event.
     * @private
     */
    async onExportPNGClick() {
        if (this.bpmnApi && this.bpmnApi.exportPNG) {
            const pngBlob = await this.bpmnApi.exportPNG();
            if (pngBlob) {
                this._downloadBlobFile(pngBlob, "png", "image/png");
            }
        } else {
            console.error("BPMN modeler not ready yet");
        }
    }

    /**
     * Handles the export PDF click event.
     * @private
     */
    async onExportPDFClick() {
        if (this.bpmnApi && this.bpmnApi.exportPDF) {
            const pdfBlob = await this.bpmnApi.exportPDF();
            if (pdfBlob) {
                this._downloadBlobFile(pdfBlob, "pdf", "application/pdf");
            }
        } else {
            console.error("BPMN modeler not ready yet");
        }
    }

    /**
     * Updates validation statistics.
     * @param {Object} stats The validation statistics.
     * @private
     */
    _onValidationChange(stats) {
        this.state.validationStats = stats;
    }

    /**
     * Updates validation statistics from the modeler.
     * @private
     */
    _updateValidationStats() {
        if (this.bpmnApi && this.bpmnApi.getValidationStats) {
            const stats = this.bpmnApi.getValidationStats();
            if (stats) {
                this.state.validationStats = stats;
            }
        }
    }

    /**
     * Handles the zoom in click event.
     * @private
     */
    onZoomInClick() {
        if (this.bpmnApi && this.bpmnApi.zoomIn) {
            this.bpmnApi.zoomIn();
        }
    }

    /**
     * Handles the zoom out click event.
     * @private
     */
    onZoomOutClick() {
        if (this.bpmnApi && this.bpmnApi.zoomOut) {
            this.bpmnApi.zoomOut();
        }
    }

    /**
     * Handles the zoom fit click event.
     * @private
     */
    onZoomFitClick() {
        if (this.bpmnApi && this.bpmnApi.zoomFit) {
            this.bpmnApi.zoomFit();
        }
    }

    /**
     * Handles the zoom reset click event.
     * @private
     */
    onZoomResetClick() {
        if (this.bpmnApi && this.bpmnApi.zoomReset) {
            this.bpmnApi.zoomReset();
        }
    }

    /**
     * Downloads the BPMN XML as a .bpmn file.
     * @param {String} xmlContent The BPMN XML string.
     * @private
     */
    _downloadBpmnFile(xmlContent) {
        // Get diagram name from record or use default
        const diagramName = this.props.record?.data?.name || "diagram";
        const fileName = `${diagramName.replace(/[^a-z0-9]/gi, "_")}.bpmn`;

        const blob = new Blob([xmlContent], {type: "application/xml"});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**
     * Downloads the SVG as a .svg file.
     * @param {String} svg The SVG string.
     * @private
     */
    _downloadSVGFile(svg) {
        // Get diagram name from record or use default
        const diagramName = this.props.record?.data?.name || "diagram";
        const fileName = `${diagramName.replace(/[^a-z0-9]/gi, "_")}.svg`;

        const blob = new Blob([svg], {type: "image/svg+xml"});
        this._downloadBlobFile(blob, "svg", "image/svg+xml", fileName);
    }

    /**
     * Downloads a blob as a file.
     * @param {Blob} blob The blob to download.
     * @param {String} extension The file extension.
     * @param {String} mimeType The MIME type.
     * @param {String} fileName Optional custom file name.
     * @private
     */
    _downloadBlobFile(blob, extension, mimeType, fileName = null) {
        // Get diagram name from record or use default
        const diagramName = this.props.record?.data?.name || "diagram";
        const finalFileName =
            fileName || `${diagramName.replace(/[^a-z0-9]/gi, "_")}.${extension}`;

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = finalFileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

registry.category("fields").add("bpmn_modeler", BpmnModelerWidget);
