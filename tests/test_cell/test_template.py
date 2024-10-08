"""Unit tests for template.py module."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from bluecellulab.cell.template import NeuronTemplate, public_hoc_cell
from bluecellulab.circuit.circuit_access import EmodelProperties
from bluecellulab.exceptions import BluecellulabError


examples_dir = Path(__file__).resolve().parent.parent / "examples"

hipp_hoc_path = (
    examples_dir
    / "hippocampus_opt_cell_template"
    / "electrophysiology"
    / "cell.hoc"
)
hipp_morph_path = (
    examples_dir / "hippocampus_opt_cell_template" / "morphology" / "cell.asc"
)

v6_hoc_path = (
    examples_dir / "circuit_sonata_quick_scx" / "components" / "hoc" / "cADpyr_L2TPC.hoc"
)

v6_morph_path = (
    examples_dir / "circuit_sonata_quick_scx" / "components" / "morphologies" / "asc" / "rr110330_C3_idA.asc"
)


def test_get_cell_with_bluepyopt_template():
    """Unit test for the get_cell method with bluepyopt_template."""
    template = NeuronTemplate(hipp_hoc_path, hipp_morph_path, "bluepyopt", None)
    cell = template.get_cell(gid=None)
    assert cell.hname() == f"bACnoljp_bluecellulab_{(hex(id(template)))}[0]"


def test_neuron_template_init():
    """Unit test for the NeuronTemplate's constructor."""
    missing_file = "missing_file"

    with pytest.raises(FileNotFoundError):
        NeuronTemplate(missing_file, hipp_morph_path, "bluepyopt", None)
    with pytest.raises(FileNotFoundError):
        NeuronTemplate(hipp_hoc_path, missing_file, "bluepyopt", None)

    NeuronTemplate(hipp_hoc_path, hipp_morph_path, "bluepyopt", None)


def test_public_hoc_cell_bluepyopt_template():
    """Unit test for public_hoc_cell."""
    template = NeuronTemplate(hipp_hoc_path, hipp_morph_path, "bluepyopt", None)
    cell = template.get_cell(None)
    hoc_public = public_hoc_cell(cell)
    assert hoc_public.gid == 0.0


def test_public_hoc_cell_v6_template():
    """Unit test for public_hoc_cell."""
    emodel_properties = EmodelProperties(
        threshold_current=1.1433533430099487,
        holding_current=1.4146618843078613,
        AIS_scaler=1.4561502933502197,
        soma_scaler=1.0
    )
    template = NeuronTemplate(v6_hoc_path, v6_morph_path, "v6", emodel_properties)
    cell = template.get_cell(5)
    hoc_public = public_hoc_cell(cell)
    assert hoc_public.gid == 5.0


def test_public_hoc_cell_v6_template_raises_bluecellulaberror():
    """Test when NeuronTemplate constructor raises a BluecellulabError."""
    with pytest.raises(BluecellulabError) as excinfo:
        template = NeuronTemplate(v6_hoc_path, v6_morph_path, "v6", emodel_properties=None)
        cell = template.get_cell(5)
    assert "EmodelProperties must be provided for template format v6 that specifies _NeededAttributes" in str(excinfo.value)


def test_public_hoc_cell_failure():
    """Unit test for public_hoc_cell when neither getCell nor CellRef is provided."""
    cell_without_getCell_or_CellRef = Mock(spec=[])  # spec=[] ensures no attributes exist
    with pytest.raises(BluecellulabError) as excinfo:
        public_hoc_cell(cell_without_getCell_or_CellRef)
    assert "Public cell properties cannot be accessed" in str(excinfo.value)


def test_load_bpo_template():
    """Test the loading of a hoc without getCell or gid."""
    hoc_path = examples_dir / "bpo_cell" / "0_cADpyr_L5TPC_a6e707a_1_sNone.hoc"
    morph_path = examples_dir / "bpo_cell" / "C060114A5.asc"
    neuron_template = NeuronTemplate(hoc_path, morph_path, "bluepyopt", None)
    cell = neuron_template.get_cell(None)
    assert len(cell.soma[0].children()) == 11
