# Project Title

## Description

[Provide a brief description of the project, its purpose, and its main features.]

## IAIA Prototype

IAIA is a Streamlit prototype that statically analyzes Python projects, reconstructs dependencies, explores potential blast radius, and produces grounded modernization guidance. Uploaded code is parsed with `ast`; it is never imported or executed.

### Windows Quick Start

To get started with IAIA on a Windows environment, follow these steps:

```powershell
cd C:\Users\z005caxw\Desktop\IAIA
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

Open the URL displayed by Streamlit and choose **Load synthetic demonstration project**, then **Analyze project**. The demo is synthetic test data and is not executed by IAIA.

### Safety and Limitations

IAIA never runs uploaded scripts, installers, binaries, builds, or network actions. Findings are indicators, not proof of vulnerabilities or a certified industrial cybersecurity assessment. Recommendations, target architecture, and migration plans require engineer review. No external AI call is made by the included provider boundary; an API key alone does not enable transmission.

## Features

- Secure ZIP validation and isolated extraction with traversal, link, size, and file-count protections.
- AST-only Python module, finding, import, complexity, and architecture analysis.
- NetworkX dependency graphs, cycles, hotspots, and explainable potential blast-radius traversal.
- Deterministic rule-based recommendations when AI is disabled.
- Review-only target architecture proposals and phased modernization actions.
- Escaped JSON and HTML report downloads.

## Installation

[Provide instructions for installing the project, including any prerequisites.]

## Usage

[Explain how to use the project, including examples and code snippets.]

## Contributing

[Provide guidelines for contributing to the project, including how to submit issues and pull requests.]

## License

[Specify the license under which the project is distributed.]

## Contact

[Provide contact information for the project maintainers or a link to a support forum.]