# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestDmnTemplateWizard(TransactionCase):
    """Test cases for DMN Template Wizard model."""

    def setUp(self):
        super().setUp()
        self.DmnTemplateWizard = self.env["dmn.template.wizard"]
        self.DmnTemplate = self.env["dmn.template"]
        self.DmnDiagram = self.env["dmn.diagram"]

        # Sample DMN XML
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
</dmn:definitions>"""

        # Create test template
        self.test_template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "description": "Test template description",
                "xml_content": self.sample_xml,
                "active": True,
            }
        )

    def test_create_wizard(self):
        """Test creating a wizard."""
        wizard = self.DmnTemplateWizard.create(
            {
                "template_id": self.test_template.id,
                "name": "New Diagram",
                "description": "New diagram description",
            }
        )

        self.assertEqual(wizard.template_id, self.test_template)
        self.assertEqual(wizard.name, "New Diagram")
        self.assertEqual(wizard.description, "New diagram description")

    def test_wizard_domain_active_templates(self):
        """Test that wizard domain filters only active templates."""
        active_template = self.DmnTemplate.create(
            {
                "name": "Active Template",
                "xml_content": self.sample_xml,
                "active": True,
            }
        )
        inactive_template = self.DmnTemplate.create(
            {
                "name": "Inactive Template",
                "xml_content": self.sample_xml,
                "active": False,
            }
        )

        wizard = self.DmnTemplateWizard.new({})
        domain = wizard._fields["template_id"].domain
        if callable(domain):
            domain = domain(wizard)

        # Domain should filter active templates
        available_templates = self.DmnTemplate.search(domain)
        self.assertIn(active_template, available_templates)
        self.assertNotIn(inactive_template, available_templates)

    def test_default_get_with_template(self):
        """Test default_get when template_id is provided."""
        wizard = self.DmnTemplateWizard.with_context(
            default_template_id=self.test_template.id
        ).new({})

        defaults = wizard.default_get(["template_id", "name"])
        self.assertEqual(defaults.get("template_id"), self.test_template.id)
        # Name should be set from template
        self.assertEqual(defaults.get("name"), self.test_template.name)

    def test_onchange_template_id(self):
        """Test onchange when template_id changes."""
        wizard = self.DmnTemplateWizard.new(
            {
                "template_id": self.test_template.id,
            }
        )

        wizard._onchange_template_id()

        self.assertEqual(wizard.name, self.test_template.name)
        self.assertEqual(wizard.description, self.test_template.description)

    def test_action_create_diagram(self):
        """Test creating a diagram from wizard."""
        wizard = self.DmnTemplateWizard.create(
            {
                "template_id": self.test_template.id,
                "name": "New Diagram",
                "description": "New diagram description",
            }
        )

        action = wizard.action_create_diagram()

        # Check action return
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "dmn.diagram")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "current")

        # Check that diagram was created
        diagram_id = action["res_id"]
        diagram = self.DmnDiagram.browse(diagram_id)

        self.assertEqual(diagram.name, "New Diagram")
        self.assertEqual(diagram.description, "New diagram description")
        self.assertEqual(diagram.dmn_xml, self.test_template.xml_content)
        self.assertEqual(diagram.template_id, self.test_template)
        self.assertEqual(diagram.version, "1.0.0")
        self.assertEqual(diagram.state, "draft")

    def test_action_create_diagram_without_description(self):
        """Test creating a diagram without description."""
        wizard = self.DmnTemplateWizard.create(
            {
                "template_id": self.test_template.id,
                "name": "New Diagram",
            }
        )

        action = wizard.action_create_diagram()

        diagram_id = action["res_id"]
        diagram = self.DmnDiagram.browse(diagram_id)

        self.assertEqual(diagram.name, "New Diagram")
        self.assertFalse(diagram.description)

    def test_action_create_diagram_multiple_times(self):
        """Test creating multiple diagrams from wizard."""
        wizard = self.DmnTemplateWizard.create(
            {
                "template_id": self.test_template.id,
                "name": "Diagram 1",
            }
        )

        action1 = wizard.action_create_diagram()
        diagram1 = self.DmnDiagram.browse(action1["res_id"])

        # Create another diagram with same wizard
        wizard.write({"name": "Diagram 2"})
        action2 = wizard.action_create_diagram()
        diagram2 = self.DmnDiagram.browse(action2["res_id"])

        self.assertNotEqual(diagram1.id, diagram2.id)
        self.assertEqual(diagram1.name, "Diagram 1")
        self.assertEqual(diagram2.name, "Diagram 2")
        self.assertEqual(diagram1.template_id, self.test_template)
        self.assertEqual(diagram2.template_id, self.test_template)
