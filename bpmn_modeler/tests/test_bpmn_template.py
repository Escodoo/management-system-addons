# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestBpmnTemplate(TransactionCase):
    """Test cases for BPMN Template model."""

    def setUp(self):
        super().setUp()
        self.BpmnTemplate = self.env["bpmn.template"]
        self.BpmnTemplateCategory = self.env["bpmn.template.category"]
        self.BpmnDiagram = self.env["bpmn.diagram"]

        # Create test category
        self.test_category = self.BpmnTemplateCategory.create(
            {
                "name": "Test Category",
                "description": "Test category description",
            }
        )

        # Sample BPMN XML
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
</bpmn:definitions>"""

    def test_create_template(self):
        """Test creating a BPMN template."""
        template = self.BpmnTemplate.create(
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
        template = self.BpmnTemplate.create(
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
        template1 = self.BpmnTemplate.create(
            {
                "name": "Template A",
                "xml_content": self.sample_xml,
                "sequence": 20,
            }
        )
        template2 = self.BpmnTemplate.create(
            {
                "name": "Template B",
                "xml_content": self.sample_xml,
                "sequence": 10,
            }
        )
        template3 = self.BpmnTemplate.create(
            {
                "name": "Template C",
                "xml_content": self.sample_xml,
                "sequence": 10,
            }
        )

        # Search only for the templates created in this test
        templates = self.BpmnTemplate.search(
            [("id", "in", [template1.id, template2.id, template3.id])]
        )
        # Should be ordered by sequence (10, 10, 20) then name (B, C, A)
        self.assertEqual(templates[0], template2)  # sequence 10, name B
        self.assertEqual(templates[1], template3)  # sequence 10, name C
        self.assertEqual(templates[2], template1)  # sequence 20, name A

    def test_compute_usage_count(self):
        """Test computation of usage_count field."""
        template = self.BpmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
            }
        )

        # Initially should be 0
        self.assertEqual(template.usage_count, 0)

        # Create diagrams using this template
        diagram1 = self.BpmnDiagram.create(
            {
                "name": "Diagram 1",
                "template_id": template.id,
            }
        )
        diagram2 = self.BpmnDiagram.create(
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
        template = self.BpmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
            }
        )

        action = template.action_use_template()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "bpmn.diagram")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "current")
        self.assertEqual(action["context"]["default_name"], "Test Template")
        self.assertEqual(action["context"]["default_bpmn_xml"], self.sample_xml)
        self.assertEqual(action["context"]["default_template_id"], template.id)

    def test_template_active_filter(self):
        """Test filtering active templates."""
        active_template = self.BpmnTemplate.create(
            {
                "name": "Active Template",
                "xml_content": self.sample_xml,
                "active": True,
            }
        )
        inactive_template = self.BpmnTemplate.create(
            {
                "name": "Inactive Template",
                "xml_content": self.sample_xml,
                "active": False,
            }
        )

        active_templates = self.BpmnTemplate.search([("active", "=", True)])
        self.assertIn(active_template, active_templates)
        self.assertNotIn(inactive_template, active_templates)

    def test_template_public_filter(self):
        """Test filtering public templates."""
        public_template = self.BpmnTemplate.create(
            {
                "name": "Public Template",
                "xml_content": self.sample_xml,
                "is_public": True,
            }
        )
        private_template = self.BpmnTemplate.create(
            {
                "name": "Private Template",
                "xml_content": self.sample_xml,
                "is_public": False,
            }
        )

        public_templates = self.BpmnTemplate.search([("is_public", "=", True)])
        self.assertIn(public_template, public_templates)
        self.assertNotIn(private_template, public_templates)

    def test_template_category_relationship(self):
        """Test relationship between template and category."""
        template = self.BpmnTemplate.create(
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
        template = self.BpmnTemplate.create(
            {
                "name": "Test Template",
                "xml_content": self.sample_xml,
            }
        )

        self.assertFalse(template.category_id)
        self.assertTrue(template.name)
