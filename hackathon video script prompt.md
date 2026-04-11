**prompt for perplexity:** consider the following info (AND THE CODE) and make sure the track specifications and rubric (shown below) is satisfied. Create a structured **set of dot points** to mention in a 5 minute video script (the video is basically a tour of the website made). SPOT ANY ERRORS IN THE FOLLOWING SCAFFOLD AND MENTION THEM

plan so far: 

website tour 

5 min 

script: 

pitch ideas so far: 

Story telling about the risk of collisions at the start and how this is super important in reducing pollution and also for informing regulatory bodies. etc, The visuals of the website assist in this. 

The substance of the pitch should be comprehensive but direct

Every single man made satellite has been tracked \- around 25k in total (historical and active) as of april 10\. This is using 3 independent databases. 

We have collated and analysed a bunch of different features and used (see code and below for the features) to determine compliance

we have created operator reliability scores based on the percentage of compliant operated satellites. 

We applied bayesian smoothing to reduce the occurrence of extreme values for operators with low reliability. (explain this) 

Why did we do all of this? Well we dont know if every satellite is compliant or non compliant. 

There are many active satellites of unknown compliance. So we trained an ML model to determine with high accuracy the PROBABILITY THAT A GIVEN SATELLITE IS COMPLIANT.  
We trained the model based on the \~8000 known HISTORICAL satellites and split into a 80% training and 20% prediction situation. Afterwards we applied the model to the \~17000 ACTIVE satellites and collected the data.  
Now, the website has done all of this technical work primarily for one function: ‘To determine the probability of compliance of some previously unknown satellite’ 

* using the most important characteristics used to train the ML model (avg orbital height, period, operator score etc)

Immensely useful for governing space bodies who need to approve satellite launches (obviously in this case planned physical details and operator score will be considered). (more detail here) 

# **🤩 This Year’s Tracks**

## **Beyond The Horizon**

\<aside\>

*As the first track for Codebrew: Cosmos Resonance, we introduce Beyond the Horizon. In this modern era of constant innovation in the space race, there have been countless advancements made to democratize outer space and give humans a chance to explore our universe and beyond. In this track, we want contestants to showcase all your strongest skills, whether low-level programming, machine learning, app development, etc. to develop a creative solution that helps solve a problem in the current space industry. This could be anything from software for spacecraft, modelling and analysis tools, to systems which support Earth such as NASA’ SMAP. Recommended for experienced coders. Godspeed\!*

\</aside\>

The space industry in 2026 is not what it was a decade ago. Artemis II is preparing to carry humans further from Earth than any crewed mission since Apollo 17\. Private launch cadences have compressed what once took years into months. And culturally, works like Andy Weir's *Project Hail Mary* have reignited public imagination about what it means to solve impossible problems with nothing but ingenuity and the right tools. We are, standing at an inflection point.

And yet, nearly every problem worth solving in this industry has been explored in some form. That's not a dead end. That's your brief.

**Your job is to find what exists, understand why it works, and build it better.**

### **Where to Start**

Study the tools and systems already shaping the industry:

* Satellite operations and telemetry platforms  
* Mission planning and trajectory modelling software  
* Earth observation systems like NASA's SMAP or ESA's Copernicus  
* Crew support and communication systems being developed for Artemis and beyond  
* Data pipelines handling the volume coming from next-generation telescopes and deep space probes

What makes the best ones effective? Is it data accuracy? Real-time accessibility? The way they surface critical information under pressure? A specific interface decision? Find the thing that makes it work, then rebuild it with that insight at the center.

Focus on lower level products and what could be utilized to produce a technically improved and impressive product. Think about the fact that technical resources are limited and requires a superior level of optimization.

Your submission should include a working prototype and a video pitch. In your pitch, walk us through:

* The existing tool, system, or mission context you drew inspiration from  
* Your analysis of what makes it effective and where it falls short  
* The specific technical and design decisions you made based on that analysis

---

### **🏆 On-Theme Prize (Bonus Award)**

All submissions are eligible for the main Beyond the Horizon track prize. For a shot at the additional on-theme prize, reframe your perspective:

Imagine you're not building for today, you're building for the moment the modern space race is just beginning. The kind of foundational tools that Artemis mission planners, early satellite operators, or the fictional crew of the *Hail Mary* would have actually needed. One of the first platforms for managing satellite data. An early system for crew communication across deep space latency. A tool for modelling trajectories when the margin for error is everything.

The on-theme prize rewards submissions that capture not just functionality, but the weight and clarity of building something that genuinely matters, the feeling of solving a hard problem at the frontier.

# **Codebrew Rubric**

# **Judging Rubric**

Codebrew: Cosmos Resonance

---

## **Score breakdown**

| Category | Points |
| ----- | ----- |
| Technical score | /20 |
| Pitch score | /20 |
| Track-specific score | /25 |
| **Total (excl. bonus)** | **/60** |
| On-theme bonus | \+5 |
| **Total (incl. bonus)** | **/65** |

---

## **Technical score — /20**

| Criterion | Points |
| ----- | ----- |
| Functionality & completeness | 0–7 |
| Code quality & architecture | 0–7 |
| Appropriate use of technology | 0–6 |

---

## **Pitch score — /20**

| Criterion | Points |
| ----- | ----- |
| Clarity of problem & solution | 0–7 |
| Depth of analysis | 0–7 |
| Presentation quality | 0–6 |

---

## **Track-specific score — /25**

### 

### 

| Criterion | Points |
| ----- | ----- |
| **Technical depth & relevance to space industry** | **0–10** |
| **Understanding of existing tools & improvement** | **0–10** |
| **On-theme resonance *(bonus)*** | **0–5** |

# **Features Used in the Delphi ML Model**

### Based on your pipeline and feature engineering phase, here are the features used:

### ---

## **Core Features**

| Feature | What It Is | Why It Matters |
| ----- | ----- | ----- |
| avg\_altitude\_km | Average of apogee and perigee | Higher orbits are harder to deorbit due to less atmospheric drag |
| period\_min | Orbital period in minutes | Proxy for orbit size; strongly correlates with altitude |
| orbit\_class | LEO / MEO / GEO / HEO | Different orbit types have very different disposal challenges |
| inclination\_deg | Orbital inclination in degrees | Affects deorbit options and collision geometry |
| age\_years | Years since launch | Older satellites are more likely to have failed or been abandoned |
| operator\_reliability\_score | Bayesian-smoothed compliance rate of the operator | Strongest predictor — poor operator history often repeats |

### ---

## **Operator-Derived Features**

| Feature | What It Is | Why It Matters |
| ----- | ----- | ----- |
| operator\_reliability\_score | Percentage of operator’s historical satellites properly deorbited (with Bayesian smoothing) | Captures whether the operator has a pattern of responsibility or neglect |
| operator\_total\_objects | Total objects attributed to the operator | Larger operators may have more resources — or more neglected satellites |
| operator\_non\_compliant\_count | Number of dead satellites left in orbit | Direct measure of debris contribution |

### ---

## **Possible Additional Features**

### (Depending on what was available after dataset merging)

| Feature | What It Is | Why It Matters |
| ----- | ----- | ----- |
| expected\_lifetime | Design lifetime from UCS database | Indicates how long the satellite was intended to operate |
| age\_lifetime\_ratio | age\_years / expected\_lifetime | Values \> 1.0 indicate satellites past design life (overdue for disposal) |
| launch\_year | Year of launch | Newer satellites may include improved disposal planning |
| mass | Satellite mass | Heavier satellites are harder to deorbit |
| mission\_type | Communications / Earth observation / military | Some mission types show better compliance patterns |
| owner\_code | Country or entity code from SATCAT | Some national programs have stronger track records |

### ---

## **What the Model Actually Learns**

### In plain English, the model is learning:

### **“Given a satellite at this altitude, in this orbit type, of this age, operated by an entity with this track record — how likely is it to be properly disposed of?”**

### ---

## **Most Important Features**

### The most influential predictors are likely:

* ### **operator\_reliability\_score** → strongest signal (behavioral pattern)

* ### **avg\_altitude\_km** → physics determines disposal difficulty

* ### **age\_years / age\_lifetime\_ratio** → overdue satellites are riskier

* ### **orbit\_class** → LEO benefits from drag; GEO does not

### ---

## **How to Confirm Exactly Which Features Were Used**

### Check your model training code. It will typically look like:

### feature\_cols \= \[

###    "avg\_altitude\_km",

###    "period\_min",

###    "inclination\_deg",

###    "age\_years",

###    "orbit\_class",

###    "operator\_reliability\_score",

###    "operator\_total\_objects",

###    "age\_lifetime\_ratio",

###    "launch\_year"

### \]

### 

### X \= training\_data\[feature\_cols\]

### y \= training\_data\["compliance\_label"\]

### Whatever appears in `feature_cols` is the **definitive feature set** used by the model.

### If available, **feature importance metrics** or **SHAP values** can further confirm which features had the greatest impact on predictions.

### 
