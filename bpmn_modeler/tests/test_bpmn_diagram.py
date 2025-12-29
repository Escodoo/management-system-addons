# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestBpmnDiagram(TransactionCase):
    """Test cases for BPMN Diagram model."""

    def setUp(self):
        super().setUp()
        self.BpmnDiagram = self.env["bpmn.diagram"]
        self.BpmnDiagramCategory = self.env["bpmn.diagram.category"]
        self.BpmnTemplate = self.env["bpmn.template"]
        self.BpmnDiagramVersion = self.env["bpmn.diagram.version"]
        self.test_user = self.env.ref("base.user_admin")

        # Create test category
        self.test_category = self.BpmnDiagramCategory.create(
            {
                "name": "Test Category",
                "description": "Test category description",
            }
        )

        # Create test template
        self.test_template = self.BpmnTemplate.create(
            {
                "name": "Test Template",
                "description": "Test template description",
                "xml_content": """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  id="Definitions_1"
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="false">
    <bpmn:startEvent id="StartEvent_1"/>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1" />
  </bpmndi:BPMNDiagram>
</bpmn:definitions>""",
            }
        )

    def test_create_diagram(self):
        """Test creating a BPMN diagram."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "description": "Test description",
                "version": "1.0.0",
                "category_id": self.test_category.id,
            }
        )

        self.assertEqual(diagram.name, "Test Diagram")
        self.assertEqual(diagram.description, "Test description")
        self.assertEqual(diagram.version, "1.0.0")
        self.assertEqual(diagram.state, "draft")
        self.assertEqual(diagram.category_id, self.test_category)
        self.assertTrue(diagram.bpmn_xml)  # Should have default XML

    def test_create_diagram_from_template(self):
        """Test creating a diagram from a template."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Diagram from Template",
                "bpmn_xml": self.test_template.xml_content,
                "template_id": self.test_template.id,
                "version": "1.0.0",
            }
        )

        self.assertEqual(diagram.template_id, self.test_template)
        self.assertEqual(diagram.bpmn_xml, self.test_template.xml_content)

    def test_diagram_default_values(self):
        """Test default values for diagram."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        self.assertEqual(diagram.state, "draft")
        self.assertEqual(diagram.version, "1.0.0")
        self.assertTrue(diagram.bpmn_xml)  # Should have default XML

    def test_action_submit_for_review(self):
        """Test submitting diagram for review."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "draft",
            }
        )

        result = diagram.action_submit_for_review()
        self.assertTrue(result)
        self.assertEqual(diagram.state, "review")

    def test_action_submit_for_review_invalid_state(self):
        """Test submitting for review from invalid state."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "approved",
            }
        )

        with self.assertRaises(UserError):
            diagram.action_submit_for_review()

    def test_action_approve(self):
        """Test approving a diagram."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "review",
            }
        )

        result = diagram.action_approve()
        self.assertTrue(result)
        self.assertEqual(diagram.state, "approved")
        self.assertEqual(diagram.approval_user_id, self.env.user)
        self.assertTrue(diagram.approval_date)

    def test_action_approve_from_draft(self):
        """Test approving a diagram from draft state."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "draft",
            }
        )

        result = diagram.action_approve()
        self.assertTrue(result)
        self.assertEqual(diagram.state, "approved")

    def test_action_approve_invalid_state(self):
        """Test approving from invalid state."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "active",
            }
        )

        with self.assertRaises(UserError):
            diagram.action_approve()

    def test_action_activate(self):
        """Test activating a diagram."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "approved",
            }
        )

        result = diagram.action_activate()
        self.assertTrue(result)
        self.assertEqual(diagram.state, "active")

    def test_action_activate_invalid_state(self):
        """Test activating from invalid state."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "draft",
            }
        )

        with self.assertRaises(UserError):
            diagram.action_activate()

    def test_action_archive(self):
        """Test archiving a diagram."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "active",
            }
        )

        result = diagram.action_archive()
        self.assertTrue(result)
        self.assertEqual(diagram.state, "archived")

    def test_action_unarchive(self):
        """Test unarchiving a diagram."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "archived",
            }
        )

        result = diagram.action_unarchive()
        self.assertTrue(result)
        self.assertEqual(diagram.state, "draft")

    def test_write_protected_fields_in_draft(self):
        """Test editing protected fields when in draft state."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "draft",
            }
        )

        # Should be able to edit protected fields in draft
        diagram.write(
            {
                "name": "Updated Name",
                "description": "Updated description",
                "bpmn_xml": "<test>new xml</test>",
                "category_id": self.test_category.id,
            }
        )

        self.assertEqual(diagram.name, "Updated Name")
        self.assertEqual(diagram.description, "Updated description")
        self.assertEqual(diagram.bpmn_xml, "<test>new xml</test>")
        self.assertEqual(diagram.category_id, self.test_category)

    def test_write_protected_fields_not_in_draft(self):
        """Test that protected fields cannot be edited when not in draft."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "approved",
            }
        )

        # Should not be able to edit protected fields when not in draft
        with self.assertRaises(UserError):
            diagram.write({"name": "Updated Name"})

        with self.assertRaises(UserError):
            diagram.write({"bpmn_xml": "<test>new xml</test>"})

        # Should be able to edit non-protected fields
        diagram.write({"state": "active"})
        self.assertEqual(diagram.state, "active")

    def test_version_history_creation(self):
        """Test that version history is created when BPMN XML changes."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "bpmn_xml": "<original>xml</original>",
                "version": "1.0.0",
            }
        )

        initial_version_count = len(diagram.version_history_ids)

        # Change BPMN XML
        new_xml = "<updated>xml</updated>"
        diagram.write({"bpmn_xml": new_xml})

        # Check that version history was created
        self.assertEqual(len(diagram.version_history_ids), initial_version_count + 1)
        version_history = diagram.version_history_ids[0]
        self.assertEqual(version_history.version, "1.0.0")
        self.assertEqual(version_history.bpmn_xml, "<original>xml</original>")
        self.assertEqual(version_history.user_id, self.env.user)

    def test_version_history_not_created_on_first_write(self):
        """Test that version history is not created on first write if no previous XML."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        # Write XML for the first time (no previous XML)
        diagram.write({"bpmn_xml": "<first>xml</first>"})

        # Should not create version history if there was no previous XML
        self.assertEqual(len(diagram.version_history_ids), 0)

    def test_version_history_not_created_if_xml_unchanged(self):
        """Test that version history is not created if XML doesn't change."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
                "bpmn_xml": "<test>xml</test>",
            }
        )

        initial_version_count = len(diagram.version_history_ids)

        # Write same XML
        diagram.write({"bpmn_xml": "<test>xml</test>"})

        # Should not create version history
        self.assertEqual(len(diagram.version_history_ids), initial_version_count)

    def test_compute_last_modified(self):
        """Test computation of last_modified field."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        self.assertTrue(diagram.last_modified)
        self.assertEqual(diagram.last_modified, diagram.create_date)

        # Update the record
        diagram.write({"state": "review"})
        self.assertTrue(diagram.last_modified)
        self.assertEqual(diagram.last_modified, diagram.write_date)

    def test_compute_statistics(self):
        """Test computation of statistics."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        # Element count should be initialized to 0
        self.assertEqual(diagram.element_count, 0)

    def test_diagram_tracking(self):
        """Test that diagram fields are tracked."""
        diagram = self.BpmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        # Check that tracking fields exist (inherited from mail.thread)
        self.assertTrue(hasattr(diagram, "message_ids"))
        self.assertTrue(hasattr(diagram, "activity_ids"))

    def test_diagram_ordering(self):
        """Test that diagrams are ordered by create_date desc."""
        diagram1 = self.BpmnDiagram.create({"name": "Diagram 1"})
        diagram2 = self.BpmnDiagram.create({"name": "Diagram 2"})

        diagrams = self.BpmnDiagram.search([])
        # Most recent should be first
        self.assertEqual(diagrams[0], diagram2)
        self.assertEqual(diagrams[1], diagram1)
