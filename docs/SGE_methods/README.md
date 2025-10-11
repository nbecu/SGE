# SGE Methods Documentation

This directory contains the automatically generated SGE methods documentation.

## Files

- **`sge_methods_catalog.html`** - Interactive HTML documentation with advanced filtering and search capabilities
- **`sge_methods_catalog.json`** - Complete method catalog in JSON format for programmatic access
- **`sge_methods_snippets.json`** - VS Code/Cursor snippets for code completion

## Generation

The documentation is generated using `SGMethodsCatalog.py` located in `mainClasses/`:

```python
from mainClasses.SGMethodsCatalog import SGMethodsCatalog

catalog = SGMethodsCatalog()
catalog.generate_catalog()
catalog.save_to_json("docs/SGE_methods/sge_methods_catalog.json")
catalog.generate_html("docs/SGE_methods/sge_methods_catalog.html")
catalog.generate_snippets("docs/SGE_methods/sge_methods_snippets.json")
```

## Usage

- **HTML Interface**: Open `sge_methods_catalog.html` in a web browser for interactive exploration
- **JSON Data**: Use `sge_methods_catalog.json` for programmatic access to method information
- **Code Snippets**: Import `sge_methods_snippets.json` into VS Code/Cursor for enhanced code completion

## Method Categories

Methods are organized into logical categories:
- **NEW/ADD/SET**: Creation and modification methods
- **DELETE**: Removal methods  
- **GET/NB**: Retrieval and counting methods
- **IS/HAS**: Boolean test methods
- **DO/DISPLAY**: Action and display methods
- **OTHER**: Additional modeler methods

The catalog includes inherited methods from parent classes, providing a complete view of available functionality for each entity type.
