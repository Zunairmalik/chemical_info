import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import pubchempy as pcp




from flask import Flask, render_template, request
import pubchempy as pcp

app = Flask(__name__)

def to_subscript(formula):
    subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return formula.translate(subscript_map)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        chemical_name = request.form["chemical_name"].strip()
        try:
            compound = pcp.get_compounds(chemical_name, "name")[0]

            iupac_name = compound.iupac_name or "Not available"
            synonyms_lower = [s.lower() for s in compound.synonyms]

            # Check agar input ya iupac_name synonyms mein same hain
            if chemical_name.lower() in synonyms_lower and chemical_name.lower() == iupac_name.lower():
                alt_iupac = None
                for syn in compound.synonyms:
                    if syn.lower() != chemical_name.lower():
                        alt_iupac = syn
                        break
                if alt_iupac:
                    iupac_name = alt_iupac

            # Common name
            common_name = None
            for syn in compound.synonyms:
                if syn.lower() != iupac_name.lower():
                    common_name = syn
                    break
            if not common_name:
                common_name = chemical_name

            result = {
                "iupac_name": iupac_name,
                "common_name": common_name,
                "molecular_weight": compound.molecular_weight,
                "formula": to_subscript(compound.molecular_formula)
            }
        except (IndexError, AttributeError):
            error = f"No information found for '{chemical_name}'."

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)