#!/bin/bash

#Poseidon

python3 -m complexity_visualizer.cli.build_graph_cli \
           --from ./from/poseidon \
           --out ./dist/poseidon/poseidon_graph.json \
           --include-prefix com.totalenergies.poseidon2

python3 -m complexity_visualizer.cli.convert_cli \
           --in dist/poseidon/poseidon_graph.json \
           --out dist/poseidon/poseidon_codecharta.json \
           --project poseidon

#Asphaltor

python3 -m complexity_visualizer.cli.build_graph_cli \
           --from ./from/asphaltor \
           --out ./dist/asphaltor/asphaltor_graph.json \
           --include-prefix com.totalenergies.asphaltor

python3 -m complexity_visualizer.cli.convert_cli \
           --in dist/asphaltor/asphaltor_graph.json \
           --out dist/asphaltor/asphaltor_codecharta.json \
           --project asphaltor

#MyCfr

python3 -m complexity_visualizer.cli.build_graph_cli \
           --from ./from/mycfr \
           --out ./dist/mycfr/mycfr_graph.json \
           --include-prefix com.totalenergies.mycfr.bff

python3 -m complexity_visualizer.cli.convert_cli \
           --in dist/mycfr/mycfr_graph.json \
           --out dist/mycfr/mycfr_codecharta.json \
           --project mycfr