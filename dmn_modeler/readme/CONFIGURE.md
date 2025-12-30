# Configuration

## Installation

* Add `dmn_modeler` to your Odoo addons path.
* Install the module from the Odoo Apps menu.
* The `dmn-js` library (version 17.5.0) is included in the module assets.

## Access Rights

* Users need appropriate access rights to create and edit DMN diagrams.
* Access rights are configured in the `security/ir.model.access.csv` file.
* By default, all users can read, write, create, and unlink DMN diagrams.

## Categories

* Navigate to **DMN > Diagram Categories** to create custom categories.
* Categories help organize decision tables by business area or purpose.
* Use categories to filter and group related decision tables.

## Templates

* Navigate to **DMN > Template Categories** to organize templates.
* Create custom templates for frequently used decision patterns.
* Templates can be marked as public (available to all users) or private.

## States and Workflow

The module supports the following states for decision tables:

* **Draft**: Initial state, allows full editing of the decision table.
* **Under Review**: Diagram is submitted for review, editing is restricted.
* **Approved**: Diagram has been approved, ready for activation.
* **Active**: Diagram is in use, editing is restricted.
* **Archived**: Diagram is no longer active.

