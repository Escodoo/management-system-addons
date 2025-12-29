# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestBpmnDiagramVersion(TransactionCase):
    """Test cases for BPMN Diagram Version model."""

    def setUp(self):
        super().setUp()
        self.BpmnDiagramVersion = self.env["bpmn.diagram.version"]
        self.BpmnDiagram = self.env["bpmn.diagram"]

    def test_create_version(self):
        """Test creating a version history entry."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "bpmn_xml": "<original>xml</original>",
                "version": "1.0.0",
            }
        )

        version = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram.id,
                "version": "1.0.0",
                "bpmn_xml": "<original>xml</original>",
                "change_note": "Initial version",
            }
        )

        self.assertEqual(version.diagram_id, diagram)
        self.assertEqual(version.version, "1.0.0")
        self.assertEqual(version.bpmn_xml, "<original>xml</original>")
        self.assertEqual(version.user_id, self.env.user)
        self.assertTrue(version.change_date)
        self.assertEqual(version.change_note, "Initial version")

    def test_version_default_values(self):
        """Test default values for version."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        version = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram.id,
                "version": "1.0.0",
                "bpmn_xml": "<test>xml</test>",
            }
        )

        self.assertEqual(version.user_id, self.env.user)
        self.assertTrue(version.change_date)
        self.assertFalse(version.change_note)

    def test_version_ordering(self):
        """Test that versions are ordered by change_date desc."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        # Create first version
        version1 = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram.id,
                "version": "1.0.0",
                "bpmn_xml": "<v1>xml</v1>",
            }
        )

        # Wait a bit and create second version
        import time

        time.sleep(0.1)

        version2 = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram.id,
                "version": "2.0.0",
                "bpmn_xml": "<v2>xml</v2>",
            }
        )

        versions = self.BpmnDiagramVersion.search([("diagram_id", "=", diagram.id)])
        # Most recent should be first
        self.assertEqual(versions[0], version2)
        self.assertEqual(versions[1], version1)

    def test_version_cascade_delete(self):
        """Test that versions are deleted when diagram is deleted."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        version = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram.id,
                "version": "1.0.0",
                "bpmn_xml": "<test>xml</test>",
            }
        )

        version_id = version.id
        diagram.unlink()

        # Version should be deleted (cascade)
        self.assertFalse(self.BpmnDiagramVersion.browse(version_id).exists())

    def test_version_with_change_note(self):
        """Test version with change note."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        version = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram.id,
                "version": "1.0.0",
                "bpmn_xml": "<test>xml</test>",
                "change_note": "Fixed bug in process flow",
            }
        )

        self.assertEqual(version.change_note, "Fixed bug in process flow")

    def test_version_multiple_diagrams(self):
        """Test versions for multiple diagrams."""
        diagram1 = self.BpmnDiagram.create(
            {
                "name": "Diagram 1",
            }
        )
        diagram2 = self.BpmnDiagram.create(
            {
                "name": "Diagram 2",
            }
        )

        version1 = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram1.id,
                "version": "1.0.0",
                "bpmn_xml": "<d1>xml</d1>",
            }
        )
        version2 = self.BpmnDiagramVersion.create(
            {
                "diagram_id": diagram2.id,
                "version": "1.0.0",
                "bpmn_xml": "<d2>xml</d2>",
            }
        )

        # Check that versions are correctly associated
        self.assertEqual(version1.diagram_id, diagram1)
        self.assertEqual(version2.diagram_id, diagram2)
        self.assertEqual(len(diagram1.version_history_ids), 1)
        self.assertEqual(len(diagram2.version_history_ids), 1)
