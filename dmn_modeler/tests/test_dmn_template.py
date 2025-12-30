# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestDmnTemplate(TransactionCase):
    """Test cases for DMN Template model."""

    def setUp(self):
        super().setUp()
        self.DmnTemplate = self.env["dmn.template"]
        self.DmnTemplateCategory = self.env["dmn.template.category"]
        self.DmnDiagram = self.env["dmn.diagram"]

        # Create test category
        self.test_category = self.DmnTemplateCategory.create(
            {
                "name": "Test Category",
                "description": "Test category description",
            }
        )

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

    def test_create_template(self):
        """Test creating a DMN template."""
        template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "description": "Test template description",
                "xml_content": self.sample_xml,
                "category_id": self.test_category.id,
                "icon": "fa-sitemap",
                "sequence": 10,
            }
        )

        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.description, "Test template description")
        self.assertEqual(template.xml_content, self.sample_xml)
        self.assertEqual(template.category_id, self.test_category)
        self.assertEqual(template.icon, "fa-sitemap")
        self.assertEqual(template.sequence, 10)
        self.assertTrue(template.is_public)
        self.assertTrue(template.active)

    def test_template_default_values(self):
        """Test default values for template."""
        template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
            }
        )

        self.assertEqual(template.icon, "fa-file-o")
        self.assertEqual(template.sequence, 10)
        self.assertTrue(template.is_public)
        self.assertTrue(template.active)

    def test_template_ordering(self):
        """Test that templates are ordered by sequence and name."""
        template1 = self.DmnTemplate.create(
            {
                "name": "Template A",
                "xml_content": self.sample_xml,
                "sequence": 20,
            }
        )
        template2 = self.DmnTemplate.create(
            {
                "name": "Template B",
                "xml_content": self.sample_xml,
                "sequence": 10,
            }
        )
        template3 = self.DmnTemplate.create(
            {
                "name": "Template C",
                "xml_content": self.sample_xml,
                "sequence": 10,
            }
        )

        # Search only for the templates created in this test
        templates = self.DmnTemplate.search(
            [("id", "in", [template1.id, template2.id, template3.id])]
        )
        # Should be ordered by sequence (10, 10, 20) then name (B, C, A)
        self.assertEqual(templates[0], template2)  # sequence 10, name B
        self.assertEqual(templates[1], template3)  # sequence 10, name C
        self.assertEqual(templates[2], template1)  # sequence 20, name A

    def test_compute_usage_count(self):
        """Test computation of usage_count field."""
        template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
            }
        )

        # Initially should be 0
        self.assertEqual(template.usage_count, 0)

        # Create diagrams using this template
        diagram1 = self.DmnDiagram.create(
            {
                "name": "Diagram 1",
                "template_id": template.id,
            }
        )
        diagram2 = self.DmnDiagram.create(
            {
                "name": "Diagram 2",
                "template_id": template.id,
            }
        )

        # Usage count should be 2
        self.assertEqual(diagram2.template_id, template)
        template.invalidate_recordset(["usage_count"])
        self.assertEqual(template.usage_count, 2)

        # Delete one diagram
        diagram1.unlink()
        template.invalidate_recordset(["usage_count"])
        self.assertEqual(template.usage_count, 1)

    def test_action_use_template(self):
        """Test action_use_template method."""
        template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
            }
        )

        action = template.action_use_template()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "dmn.diagram")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "current")
        self.assertEqual(action["context"]["default_name"], "Test Template")
        self.assertEqual(action["context"]["default_dmn_xml"], self.sample_xml)
        self.assertEqual(action["context"]["default_template_id"], template.id)

    def test_template_active_filter(self):
        """Test filtering active templates."""
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

        active_templates = self.DmnTemplate.search([("active", "=", True)])
        self.assertIn(active_template, active_templates)
        self.assertNotIn(inactive_template, active_templates)

    def test_template_public_filter(self):
        """Test filtering public templates."""
        public_template = self.DmnTemplate.create(
            {
                "name": "Public Template",
                "xml_content": self.sample_xml,
                "is_public": True,
            }
        )
        private_template = self.DmnTemplate.create(
            {
                "name": "Private Template",
                "xml_content": self.sample_xml,
                "is_public": False,
            }
        )

        public_templates = self.DmnTemplate.search([("is_public", "=", True)])
        self.assertIn(public_template, public_templates)
        self.assertNotIn(private_template, public_templates)

    def test_template_category_relationship(self):
        """Test relationship between template and category."""
        template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
                "category_id": self.test_category.id,
            }
        )

        self.assertEqual(template.category_id, self.test_category)
        self.assertIn(template, self.test_category.template_ids)

    def test_template_without_category(self):
        """Test creating template without category."""
        template = self.DmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
            }
        )

        self.assertFalse(template.category_id)
        self.assertTrue(template.name)
