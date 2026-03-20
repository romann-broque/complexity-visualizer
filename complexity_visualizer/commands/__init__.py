"""Command modules for complexity-viz CLI.

Each command is responsible for one step in the analysis pipeline:
- generate_dots: Generate .dot files using jdeps
- build_graph: Build dependency graph and compute metrics
- convert: Convert to CodeCharta format
- visualize: Open CodeCharta visualization
- run: Execute full pipeline (all steps)
"""
