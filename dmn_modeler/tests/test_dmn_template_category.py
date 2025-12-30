# Copyright 2025 - TODAY, Marcel Savegnago <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestDmnTemplateCategory(TransactionCase):
    """Test cases for DMN Template Category model."""

    def setUp(self):
        super().setUp()
        self.DmnTemplateCategory = self.env["dmn.template.category"]
        self.DmnTemplate = self.env["dmn.template"]

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

    def test_create_category(self):
        """Test creating a template category."""
        category = self.DmnTemplateCategory.create(
            {
                "name": "Test Category",
                "description": "<p>Test category description</p>",
                "sequence": 10,
            }
        )

        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.description, "<p>Test category description</p>")
        self.assertEqual(category.sequence, 10)

    def test_category_default_values(self):
        """Test default values for category."""
        category = self.DmnTemplateCategory.create(
            {
                "name": "Test Category",
            }
        )

        self.assertEqual(category.sequence, 10)

    def test_category_ordering(self):
        """Test that categories are ordered by sequence and name."""
        category1 = self.DmnTemplateCategory.create(
            {
                "name": "Category A",
                "sequence": 20,
            }
        )
        category2 = self.DmnTemplateCategory.create(
            {
                "name": "Category B",
                "sequence": 10,
            }
        )
        category3 = self.DmnTemplateCategory.create(
            {
                "name": "Category C",
                "sequence": 10,
            }
        )

        # Search only for the categories created in this test
        categories = self.DmnTemplateCategory.search(
            [("id", "in", [category1.id, category2.id, category3.id])]
        )
        # Should be ordered by sequence (10, 10, 20) then name (B, C, A)
        self.assertEqual(categories[0], category2)  # sequence 10, name B
        self.assertEqual(categories[1], category3)  # sequence 10, name C
        self.assertEqual(categories[2], category1)  # sequence 20, name A

    def test_compute_template_count(self):
        """Test computation of template_count field."""
        category = self.DmnTemplateCategory.create(
            {
                "name": "Test Category",
            }
        )

        # Initially should be 0
        self.assertEqual(category.template_count, 0)

        # Create active templates
        template1 = self.DmnTemplate.create(
            {
                "name": "Template 1",
                "xml_content": self.sample_xml,
                "category_id": category.id,
                "active": True,
            }
        )
        template2 = self.DmnTemplate.create(
            {
                "name": "Template 2",
                "xml_content": self.sample_xml,
                "category_id": category.id,
                "active": True,
            }
        )
        template3 = self.DmnTemplate.create(
            {
                "name": "Template 3",
                "xml_content": self.sample_xml,
                "category_id": category.id,
                "active": False,  # Inactive template
            }
        )

        # Template count should only count active templates
        # All templates should be associated with the category
        # Flush to ensure all writes are committed
        self.env.flush_all()
        # Verify all templates are associated with the category
        # Search directly to ensure we get all templates (including inactive)
        all_templates = self.DmnTemplate.with_context(active_test=False).search(
            [("category_id", "=", category.id)]
        )
        self.assertIn(template1, all_templates)
        self.assertIn(template2, all_templates)
        self.assertIn(template3, all_templates)
        # Invalidate cache and re-read to get fresh data for template_ids
        # One2many fields also respect active_test, so we need to disable it
        self.env.invalidate_all()
        category = self.DmnTemplateCategory.with_context(active_test=False).browse(
            category.id
        )
        # Verify template_ids field includes all templates (One2many returns all)
        self.assertIn(template1, category.template_ids)
        self.assertIn(template2, category.template_ids)
        self.assertIn(template3, category.template_ids)
        # But template_count should only count active ones
        category.invalidate_recordset(["template_count"])
        self.assertEqual(category.template_count, 2)

        # Archive one template
        template1.write({"active": False})
        category.invalidate_recordset(["template_count"])
        self.assertEqual(category.template_count, 1)

    def test_category_template_relationship(self):
        """Test relationship between category and templates."""
        category = self.DmnTemplateCategory.create(
            {
                "name": "Test Category",
            }
        )

        template1 = self.DmnTemplate.create(
            {
                "name": "Template 1",
                "xml_content": self.sample_xml,
                "category_id": category.id,
            }
        )
        template2 = self.DmnTemplate.create(
            {
                "name": "Template 2",
                "xml_content": self.sample_xml,
                "category_id": category.id,
            }
        )

        self.assertIn(template1, category.template_ids)
        self.assertIn(template2, category.template_ids)
        self.assertEqual(len(category.template_ids), 2)

    def test_category_with_html_description(self):
        """Test category with HTML description."""
        html_content = "<p>This is a <strong>bold</strong> description</p>"
        category = self.DmnTemplateCategory.create(
            {
                "name": "Test Category",
                "description": html_content,
            }
        )

        self.assertEqual(category.description, html_content)
