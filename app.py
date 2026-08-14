from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from groq import Groq
import textstat
import os


app = Flask(__name__)
CORS(app)

# ============================================================
# EXPLAINATMYLEVEL
# Adaptive Reading-Level Explainer
# ============================================================

print("=" * 55)
print("             ExplainAtMyLevel")
print("=" * 55)



api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)


# ============================================================
# AI GENERATION
# ============================================================

def generate_explanation(topic, level):

    prompts = {

        "beginner": """
Explain the topic for a complete beginner.

Rules:
- Use simple everyday vocabulary.
- Use short and clear sentences.
- Avoid unnecessary technical terms.
- If a technical term is necessary, explain it simply.
- Use a simple analogy or example when useful.
- Assume the reader has no background knowledge.
- Preserve the important facts.
- Make the explanation friendly and easy to understand.
""",

        "intermediate": """
Explain the topic for a student with basic knowledge.

Rules:
- Use moderately technical vocabulary.
- Introduce important terminology.
- Explain the important mechanisms and relationships.
- Give enough detail for a student to understand the concept.
- Avoid unnecessarily advanced academic language.
- Preserve the important facts.
""",

        "expert": """
Explain the topic for an advanced university-level reader.

Rules:
- Use precise technical terminology.
- Include mechanisms, relationships, and important technical details.
- Assume strong background knowledge.
- Use academically appropriate language.
- Explain the topic with greater technical depth.
- Preserve the important facts.
"""
    }

    prompt = f"""
You are an adaptive educational AI.

Topic:
{topic}

Target reading level:
{level}

{prompts[level]}

Return ONLY the explanation.

Do not mention the reading level.
Do not compare this explanation with other versions.
Do not say that you are an AI.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()


# ============================================================
# READABILITY
# ============================================================

def readability_score(text):
    return round(
        textstat.flesch_reading_ease(text),
        2
    )


# ============================================================
# ADAPTATION SCORE
# ============================================================

def calculate_adaptation_score(beginner_score, expert_score):

    separation = abs(
        beginner_score - expert_score
    )

    # Convert the readability gap into a 0–100 score.
    # A gap of 50 points or more represents strong adaptation.
    adaptation = min(
        100,
        (separation / 50) * 100
    )

    return round(adaptation, 2)


# ============================================================
# API ENDPOINT
# ============================================================

@app.route("/explain", methods=["POST"])
def explain():

    try:

        data = request.get_json()

        if not data or "topic" not in data:
            return jsonify({
                "error": "Topic is required."
            }), 400

        topic = data["topic"].strip()

        if not topic:
            return jsonify({
                "error": "Topic cannot be empty."
            }), 400

        # Generate three versions
        beginner = generate_explanation(
            topic,
            "beginner"
        )

        intermediate = generate_explanation(
            topic,
            "intermediate"
        )

        expert = generate_explanation(
            topic,
            "expert"
        )

        # Calculate readability
        beginner_score = readability_score(
            beginner
        )

        intermediate_score = readability_score(
            intermediate
        )

        expert_score = readability_score(
            expert
        )

        # Calculate separation
        readability_separation = round(
            abs(
                beginner_score - expert_score
            ),
            2
        )

        # Calculate adaptation
        adaptation_score = calculate_adaptation_score(
            beginner_score,
            expert_score
        )

        return jsonify({

            "beginner": beginner,

            "intermediate": intermediate,

            "expert": expert,

            "beginner_score":
                beginner_score,

            "intermediate_score":
                intermediate_score,

            "expert_score":
                expert_score,

            "readability_separation":
                readability_separation,

            "adaptation_score":
                adaptation_score

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# WEBSITE
# ============================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>ExplainAtMyLevel</title>


<style>

/* =========================================================
   GLOBAL
   ========================================================= */

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #f5f7ff,
            #eef2ff
        );

    color: #202124;

    min-height: 100vh;

}


/* =========================================================
   CONTAINER
   ========================================================= */

.container {

    max-width: 1200px;

    margin: auto;

    padding: 45px 25px 60px;

}


/* =========================================================
   HEADER
   ========================================================= */

.header {

    text-align: center;

    margin-bottom: 35px;

}

.logo {

    display: inline-block;

    font-size: 15px;

    font-weight: bold;

    letter-spacing: 2px;

    color: #6366f1;

    margin-bottom: 10px;

}

h1 {

    margin: 0;

    font-size: 46px;

    font-weight: 800;

    letter-spacing: -1px;

}

.subtitle {

    margin-top: 12px;

    color: #6b7280;

    font-size: 18px;

}


/* =========================================================
   INPUT
   ========================================================= */

.input-area {

    background: white;

    padding: 28px;

    border-radius: 20px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.07);

    margin-bottom: 30px;

}

textarea {

    width: 100%;

    min-height: 130px;

    padding: 17px;

    font-size: 16px;

    line-height: 1.6;

    border: 2px solid #e5e7eb;

    border-radius: 13px;

    resize: vertical;

    outline: none;

    transition: 0.2s;

}

textarea:focus {

    border-color: #6366f1;

}


button {

    margin-top: 16px;

    padding: 14px 25px;

    border: none;

    border-radius: 11px;

    background:
        linear-gradient(
            135deg,
            #6366f1,
            #4f46e5
        );

    color: white;

    font-size: 16px;

    font-weight: bold;

    cursor: pointer;

    transition: 0.2s;

}

button:hover {

    transform: translateY(-1px);

    box-shadow:
        0 5px 15px rgba(79,70,229,0.25);

}

button:disabled {

    opacity: 0.55;

    cursor: not-allowed;

    transform: none;

}


/* =========================================================
   STATUS
   ========================================================= */

.status {

    margin-top: 15px;

    text-align: center;

    color: #6b7280;

}

.error {

    color: #dc2626;

    text-align: center;

    margin-top: 15px;

}


/* =========================================================
   CARDS
   ========================================================= */

.cards {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 22px;

}


.card {

    background: white;

    padding: 25px;

    border-radius: 18px;

    min-height: 370px;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.06);

    position: relative;

}

.card h2 {

    margin-top: 0;

    margin-bottom: 5px;

}

.card-subtitle {

    color: #6b7280;

    font-size: 14px;

    margin-bottom: 20px;

}

.card-text {

    line-height: 1.7;

    color: #374151;

}

.beginner {

    border-top: 6px solid #22c55e;

}

.intermediate {

    border-top: 6px solid #eab308;

}

.expert {

    border-top: 6px solid #ef4444;

}


/* =========================================================
   SCORE
   ========================================================= */

.score-label {

    color: #6b7280;

    font-size: 13px;

    margin-top: 20px;

}

.score {

    font-size: 25px;

    font-weight: bold;

    margin-top: 5px;

}


/* =========================================================
   ANALYSIS
   ========================================================= */

.analysis {

    margin-top: 30px;

    background: white;

    padding: 30px;

    border-radius: 20px;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.06);

}

.analysis h2 {

    margin-top: 0;

}

.analysis-description {

    color: #6b7280;

}


/* =========================================================
   BARS
   ========================================================= */

.bar-container {

    margin-top: 25px;

}

.bar-label {

    display: flex;

    justify-content: space-between;

    font-weight: 600;

    margin-bottom: 7px;

}

.bar {

    height: 13px;

    margin-bottom: 18px;

    border-radius: 20px;

    background: #e5e7eb;

    overflow: hidden;

}

.fill {

    height: 100%;

    width: 0%;

    border-radius: 20px;

    transition:
        width 0.7s ease;

}

.beginner-fill {

    background: #22c55e;

}

.intermediate-fill {

    background: #eab308;

}

.expert-fill {

    background: #ef4444;

}


/* =========================================================
   METRICS
   ========================================================= */

.metrics {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 20px;

    margin-top: 25px;

}

.metric {

    background: #f8fafc;

    border-radius: 15px;

    padding: 22px;

}

.metric-title {

    color: #6b7280;

    font-size: 14px;

}

.metric-value {

    font-size: 30px;

    font-weight: 800;

    margin-top: 5px;

}

.adaptation {

    color: #4f46e5;

}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {

    text-align: center;

    color: #9ca3af;

    margin-top: 35px;

    font-size: 13px;

}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media(max-width: 850px) {

    .cards {

        grid-template-columns: 1fr;

    }

    .metrics {

        grid-template-columns: 1fr;

    }

    h1 {

        font-size: 36px;

    }

}

</style>

</head>


<body>


<div class="container">


<!-- =====================================================
     HEADER
     ===================================================== -->

<div class="header">

<div class="logo">
ADAPTIVE AI
</div>

<h1>
ExplainAtMyLevel
</h1>

<div class="subtitle">
Same knowledge. Different complexity.
</div>

</div>


<!-- =====================================================
     INPUT
     ===================================================== -->

<div class="input-area">

<textarea
id="topic"
placeholder="What's on your mind? Enter a topic..."
></textarea>


<button
id="generate"
onclick="generateExplanations()"
>

Generate Explanations

</button>


<div
class="status"
id="status"
></div>


<div
class="error"
id="error"
></div>

</div>


<!-- =====================================================
     EXPLANATION CARDS
     ===================================================== -->

<div class="cards">


<!-- BEGINNER -->

<div class="card beginner">

<h2>
🟢 Beginner
</h2>

<div class="card-subtitle">
Easy to read
</div>

<div
class="card-text"
id="beginner"
>
Your beginner explanation will appear here.
</div>

<div class="score-label">
Flesch Reading Ease
</div>

<div
class="score"
id="beginnerScore"
>
—
</div>

</div>


<!-- INTERMEDIATE -->

<div class="card intermediate">

<h2>
🟡 Intermediate
</h2>

<div class="card-subtitle">
Moderate complexity
</div>

<div
class="card-text"
id="intermediate"
>
Your intermediate explanation will appear here.
</div>

<div class="score-label">
Flesch Reading Ease
</div>

<div
class="score"
id="intermediateScore"
>
—
</div>

</div>


<!-- EXPERT -->

<div class="card expert">

<h2>
🔴 Expert
</h2>

<div class="card-subtitle">
Advanced
</div>

<div
class="card-text"
id="expert"
>
Your expert explanation will appear here.
</div>

<div class="score-label">
Flesch Reading Ease
</div>

<div
class="score"
id="expertScore"
>
—
</div>

</div>


</div>


<!-- =====================================================
     READABILITY ANALYSIS
     ===================================================== -->

<div class="analysis">

<h2>
📊 Readability Analysis
</h2>

<p class="analysis-description">
Higher Flesch Reading Ease scores indicate easier text.
</p>


<div class="bar-container">


<div class="bar-label">

<span>
Beginner
</span>

<span id="bValue">
—
</span>

</div>

<div class="bar">

<div
class="fill beginner-fill"
id="bBar"
></div>

</div>


<div class="bar-label">

<span>
Intermediate
</span>

<span id="iValue">
—
</span>

</div>

<div class="bar">

<div
class="fill intermediate-fill"
id="iBar"
></div>

</div>


<div class="bar-label">

<span>
Expert
</span>

<span id="eValue">
—
</span>

</div>

<div class="bar">

<div
class="fill expert-fill"
id="eBar"
></div>

</div>


</div>


<!-- =====================================================
     METRICS
     ===================================================== -->

<div class="metrics">


<div class="metric">

<div class="metric-title">
Readability Separation
</div>

<div
class="metric-value"
id="separation"
>
—
</div>

<div class="metric-title">
Points between Beginner and Expert
</div>

</div>


<div class="metric">

<div class="metric-title">
Adaptation Score
</div>

<div
class="metric-value adaptation"
id="adaptationScore"
>
—
</div>

<div class="metric-title">
Measured level differentiation
</div>

</div>


</div>


</div>


<div class="footer">

ExplainAtMyLevel · Adaptive educational AI

</div>


</div>


<script>


// =========================================================
// GENERATE EXPLANATIONS
// =========================================================

async function generateExplanations() {


    const topic =
        document
        .getElementById("topic")
        .value
        .trim();


    const button =
        document
        .getElementById("generate");


    const status =
        document
        .getElementById("status");


    const error =
        document
        .getElementById("error");


    // Validate input

    if (!topic) {

        error.textContent =
            "Please enter a topic first.";

        return;

    }


    // Reset

    error.textContent = "";

    status.textContent =
        "Generating three adaptive explanations...";

    button.disabled = true;


    try {


        const response =
            await fetch(
                "/explain",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            topic: topic
                        })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Something went wrong."
            );

        }


        // =================================================
        // EXPLANATIONS
        // =================================================

        document
            .getElementById("beginner")
            .textContent =
                data.beginner;


        document
            .getElementById("intermediate")
            .textContent =
                data.intermediate;


        document
            .getElementById("expert")
            .textContent =
                data.expert;


        // =================================================
        // SCORES
        // =================================================

        document
            .getElementById("beginnerScore")
            .textContent =
                data.beginner_score;


        document
            .getElementById("intermediateScore")
            .textContent =
                data.intermediate_score;


        document
            .getElementById("expertScore")
            .textContent =
                data.expert_score;


        // =================================================
        // BAR VALUES
        // =================================================

        document
            .getElementById("bValue")
            .textContent =
                data.beginner_score;


        document
            .getElementById("iValue")
            .textContent =
                data.intermediate_score;


        document
            .getElementById("eValue")
            .textContent =
                data.expert_score;


        // =================================================
        // READABILITY SEPARATION
        // =================================================

        document
            .getElementById("separation")
            .textContent =
                data.readability_separation;


        // =================================================
        // ADAPTATION SCORE
        // =================================================

        document
            .getElementById("adaptationScore")
            .textContent =
                data.adaptation_score + "%";


        // =================================================
        // READABILITY BARS
        // =================================================

        document
            .getElementById("bBar")
            .style.width =
                Math.max(
                    0,
                    Math.min(
                        100,
                        data.beginner_score
                    )
                ) + "%";


        document
            .getElementById("iBar")
            .style.width =
                Math.max(
                    0,
                    Math.min(
                        100,
                        data.intermediate_score
                    )
                ) + "%";


        document
            .getElementById("eBar")
            .style.width =
                Math.max(
                    0,
                    Math.min(
                        100,
                        data.expert_score
                    )
                ) + "%";


        status.textContent =
            "✓ Adaptation detected successfully.";


    }


    catch (err) {


        error.textContent =
            "Something went wrong: " +
            err.message;


        status.textContent = "";

    }


    finally {

        button.disabled = false;

    }

}

</script>


</body>

</html>

"""


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template_string(
        HTML
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("\nExplainAtMyLevel is starting...")

    print(
        "Open this address in your browser:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "\nPress CTRL+C in the terminal to stop the server."
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
