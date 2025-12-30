# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestDmnDiagram(TransactionCase):
    """Test cases for DMN Diagram model."""

    def setUp(self):
        super().setUp()
        self.DmnDiagram = self.env["dmn.diagram"]
        self.DmnDiagramCategory = self.env["dmn.diagram.category"]
        self.DmnTemplate = self.env["dmn.template"]
        self.DmnDiagramVersion = self.env["dmn.diagram.version"]
        self.test_user = self.env.ref("base.user_admin")

        # Create test category
        self.test_category = self.DmnDiagramCategory.create(
            {
                "name": "Test Category",
                "description": "Test category description",
            }
        )

        # Create test template
        self.test_template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "description": "Test template description",
                "xml_content": """<?xml version="1.0" encoding="UTF-8"?>
<dmn:definitions xmlns:dmn="https://www.omg.org/spec/DMN/20191111/MODEL/"
                xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
                xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/"
                xmlns:di="http://www.omg.org/spec/DMN/20180521/DI/"
                id="Definitions_1"
                namespace="http://camunda.org/schema/1.0/dmn"
                exporter="dmn-js"
                exporterVersion="17.5.0">
  <dmn:decision id="Decision_1" name="Decision 1">
    <dmn:decisionTable id="DecisionTable_1"/>
  </dmn:decision>
  <dmndi:DMNDI>
    <dmndi:DMNDiagram id="DMNDiagram_1">
      <dmndi:DMNShape id="DMNShape_Decision_1" dmnElementRef="Decision_1">
        <dc:Bounds height="80" width="180" x="100" y="100"/>
      </dmndi:DMNShape>
    </dmndi:DMNDiagram>
  </dmndi:DMNDI>
</dmn:definitions>""",
            }
        )

    def test_create_diagram(self):
        """Test creating a DMN diagram."""
        diagram = self.DmnDiagram.create(
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
        self.assertTrue(diagram.dmn_xml)  # Should have default XML

    def test_create_diagram_from_template(self):
        """Test creating a diagram from a template."""
        diagram = self.DmnDiagram.create(
            {
                "name": "Diagram from Template",
                "dmn_xml": self.test_template.xml_content,
                "template_id": self.test_template.id,
                "version": "1.0.0",
            }
        )

        self.assertEqual(diagram.template_id, self.test_template)
        self.assertEqual(diagram.dmn_xml, self.test_template.xml_content)

    def test_diagram_default_values(self):
        """Test default values for diagram."""
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        self.assertEqual(diagram.state, "draft")
        self.assertEqual(diagram.version, "1.0.0")
        self.assertTrue(diagram.dmn_xml)  # Should have default XML

    def test_action_submit_for_review(self):
        """Test submitting diagram for review."""
        diagram = self.DmnDiagram.create(
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
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "approved",
            }
        )

        with self.assertRaises(UserError):
            diagram.action_submit_for_review()

    def test_action_approve(self):
        """Test approving a diagram."""
        diagram = self.DmnDiagram.create(
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
        diagram = self.DmnDiagram.create(
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
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "active",
            }
        )

        with self.assertRaises(UserError):
            diagram.action_approve()

    def test_action_activate(self):
        """Test activating a diagram."""
        diagram = self.DmnDiagram.create(
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
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "draft",
            }
        )

        with self.assertRaises(UserError):
            diagram.action_activate()

    def test_action_archive(self):
        """Test archiving a diagram."""
        diagram = self.DmnDiagram.create(
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
        diagram = self.DmnDiagram.create(
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
        diagram = self.DmnDiagram.create(
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
                "dmn_xml": "<test>new xml</test>",
                "category_id": self.test_category.id,
            }
        )

        self.assertEqual(diagram.name, "Updated Name")
        self.assertEqual(diagram.description, "Updated description")
        self.assertEqual(diagram.dmn_xml, "<test>new xml</test>")
        self.assertEqual(diagram.category_id, self.test_category)

    def test_write_protected_fields_not_in_draft(self):
        """Test that protected fields cannot be edited when not in draft."""
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
                "state": "approved",
            }
        )

        # Should not be able to edit protected fields when not in draft
        with self.assertRaises(UserError):
            diagram.write({"name": "Updated Name"})

        with self.assertRaises(UserError):
            diagram.write({"dmn_xml": "<test>new xml</test>"})

        # Should be able to edit non-protected fields
        diagram.write({"state": "active"})
        self.assertEqual(diagram.state, "active")

    def test_version_history_creation(self):
        """Test that version history is created when DMN XML changes."""
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
                "dmn_xml": "<original>xml</original>",
                "version": "1.0.0",
            }
        )

        initial_version_count = len(diagram.version_history_ids)

        # Change DMN XML
        new_xml = "<updated>xml</updated>"
        diagram.write({"dmn_xml": new_xml})

        # Check that version history was created
        self.assertEqual(len(diagram.version_history_ids), initial_version_count + 1)
        version_history = diagram.version_history_ids[0]
        self.assertEqual(version_history.version, "1.0.0")
        self.assertEqual(version_history.dmn_xml, "<original>xml</original>")
        self.assertEqual(version_history.user_id, self.env.user)

    def test_version_history_not_created_on_first_write(self):
        """Test that version history is not created on first write if no previous XML."""
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        # Write XML for the first time (no previous XML)
        diagram.write({"dmn_xml": "<first>xml</first>"})

        # Should not create version history if there was no previous XML
        self.assertEqual(len(diagram.version_history_ids), 0)

    def test_version_history_not_created_if_xml_unchanged(self):
        """Test that version history is not created if XML doesn't change."""
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
                "dmn_xml": "<test>xml</test>",
            }
        )

        initial_version_count = len(diagram.version_history_ids)

        # Write same XML
        diagram.write({"dmn_xml": "<test>xml</test>"})

        # Should not create version history
        self.assertEqual(len(diagram.version_history_ids), initial_version_count)

    def test_compute_last_modified(self):
        """Test computation of last_modified field."""
        diagram = self.DmnDiagram.create(
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
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        # Element count should be initialized to 0
        self.assertEqual(diagram.element_count, 0)

    def test_diagram_tracking(self):
        """Test that diagram fields are tracked."""
        diagram = self.DmnDiagram.create(
            {
                "name": "Test Diagram",
            }
        )

        # Check that tracking fields exist (inherited from mail.thread)
        self.assertTrue(hasattr(diagram, "message_ids"))
        self.assertTrue(hasattr(diagram, "activity_ids"))

    def test_diagram_ordering(self):
        """Test that diagrams are ordered by create_date desc."""
        diagram1 = self.DmnDiagram.create({"name": "Diagram 1"})
        diagram2 = self.DmnDiagram.create({"name": "Diagram 2"})

        diagrams = self.DmnDiagram.search([])
        # Most recent should be first
        self.assertEqual(diagrams[0], diagram2)
        self.assertEqual(diagrams[1], diagram1)
