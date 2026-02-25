# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestBpmnDiagramCategory(TransactionCase):
    """Test cases for BPMN Diagram Category model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BpmnDiagramCategory = cls.env["bpmn.diagram.category"]
        cls.BpmnDiagram = cls.env["bpmn.diagram"]

    def test_create_category(self):
        """Test creating a diagram category."""
        category = self.BpmnDiagramCategory.create(
            {
                "name": "Test Category",
                "description": "Test category description",
                "sequence": 10,
            }
        )

        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.description, "Test category description")
        self.assertEqual(category.sequence, 10)

    def test_category_default_values(self):
        """Test default values for category."""
        category = self.BpmnDiagramCategory.create(
            {
                "name": "Test Category",
            }
        )

        self.assertEqual(category.sequence, 10)

    def test_category_ordering(self):
        """Test that categories are ordered by sequence and name."""
        category1 = self.BpmnDiagramCategory.create(
            {
                "name": "Category A",
                "sequence": 20,
            }
        )
        category2 = self.BpmnDiagramCategory.create(
            {
                "name": "Category B",
                "sequence": 10,
            }
        )
        category3 = self.BpmnDiagramCategory.create(
            {
                "name": "Category C",
                "sequence": 10,
            }
        )

        categories = self.BpmnDiagramCategory.search([])
        # Should be ordered by sequence (10, 10, 20) then name (B, C, A)
        self.assertEqual(categories[0], category2)  # sequence 10, name B
        self.assertEqual(categories[1], category3)  # sequence 10, name C
        self.assertEqual(categories[2], category1)  # sequence 20, name A

    def test_compute_diagram_count(self):
        """Test computation of diagram_count field."""
        category = self.BpmnDiagramCategory.create(
            {
                "name": "Test Category",
            }
        )

        # Initially should be 0
        self.assertEqual(category.diagram_count, 0)

        # Create diagrams
        diagram1 = self.BpmnDiagram.create(
            {
                "name": "Diagram 1",
                "category_id": category.id,
            }
        )
        diagram2 = self.BpmnDiagram.create(
            {
                "name": "Diagram 2",
                "category_id": category.id,
            }
        )

        # Diagram count should be 2
        self.assertIn(diagram2, category.diagram_ids)
        category.invalidate_recordset(["diagram_count"])
        self.assertEqual(category.diagram_count, 2)

        # Delete one diagram
        diagram1.unlink()
        category.invalidate_recordset(["diagram_count"])
        self.assertEqual(category.diagram_count, 1)

    def test_category_diagram_relationship(self):
        """Test relationship between category and diagrams."""
        category = self.BpmnDiagramCategory.create(
            {
                "name": "Test Category",
            }
        )

        diagram1 = self.BpmnDiagram.create(
            {
                "name": "Diagram 1",
                "category_id": category.id,
            }
        )
        diagram2 = self.BpmnDiagram.create(
            {
                "name": "Diagram 2",
                "category_id": category.id,
            }
        )

        self.assertIn(diagram1, category.diagram_ids)
        self.assertIn(diagram2, category.diagram_ids)
        self.assertEqual(len(category.diagram_ids), 2)

    def test_category_without_diagrams(self):
        """Test category without diagrams."""
        category = self.BpmnDiagramCategory.create(
            {
                "name": "Test Category",
            }
        )

        self.assertEqual(len(category.diagram_ids), 0)
        self.assertEqual(category.diagram_count, 0)
