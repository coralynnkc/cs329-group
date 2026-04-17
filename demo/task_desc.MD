# Agency-Based Named Entity Recognition in Narrative Texts

  # Background on NER
Named Entity Recognition (NER) is a foundational task in natural language processing that involves identifying and classifying spans of text corresponding to entities such as persons, locations, and organizations. Traditional NER systems operate with relatively fixed label sets (e.g., PER, LOC, ORG) and focus on extracting surface-level information about what entities are mentioned in a text. 

  # Task Description
  We introduce an extension of NER that captures  not only which entities are mentioned in a text, but the **role they play in driving events** i.e. subject-object relations.
Specifically, we define an NER task that distinguishes between entities that actively participate in events and those that are passively referenced. Our labels are stratified based on activeness, as well as type of verb, and relation to direct subject.
For example:

“Lucy opened the wardrobe.”
→ Lucy = active entity

“Edmund was captured by the Witch.”
→ Edmund = passive entity

“They spoke of Aslan in hushed tones.”
→ Aslan = mentioned indirectly

Unlike standard NER, which only extracts surface entities (e.g., PER, LOC), this task requires interpreting the semantic and syntactic role of entities within events.

  # Linguistic Context
This task operationalizes agency, a core concept in linguistics that concerns how language encodes responsibility, control, and participation in events. Agency is typically studied through:

1. thematic roles (agent, patient, experiencer)
2. transitivity and argument structure
3. voice alternations (active vs passive constructions)

In narrative texts such as The Chronicles of Narnia, agency is central to how stories are structured. Characters who are frequently mentioned are not necessarily those who drive the plot. By distinguishing between entities that act and those that are acted upon or merely referenced, this task enables linguists to analyze:

1. how agency is distributed across characters
2. how narrative focus is constructed and importance is placed
3. how perceived importance diverges from actual participation (mandela effect)

These types of tasks were not possible before the advent of LLMs. Furthermore, what modern interaction with LLMs (as shown in our research) has allowed is for linguists to be able to carry out any analysis they were previous limited to. Even if a linguist wanted to study a topic as niche as NER in the context of this one literary wor, we show how they are able to utilize growing LLM developements for their research purposes.

  # Associated Work
This task is closely related to several established NLP and linguistic annotation tasks:

1. Semantic Role Labeling (SRL): identifies roles such as agent (ARG0) and patient (ARG1) at the sentence level. This is useful especially on a psycholinguistic level to asses cognitive effect of subject-object processing.
2. Coreference Resolution: tracks entity mentions across discourse and can help improve LLM performance as well as morphological anlyses. 
3. Information Structure Analysis: examines prominence, focus, and givenness in literary and non-literary contexts with implications across corpus analysis
4. Crosslinguistic Analysis: this analysis can be used understand case and S-O structures across languages. 

# Proof of Concept 
The key contribution of this work is not redefining agency, but demonstrating that:

Large Language Models allow linguists to define and apply custom, theory-driven entity annotations—such as agency roles—without training new models or building specialized pipelines. By framing agency as a flexible NER-style task, we show that LLMs can bridge the gap between a) linguistic theory (agency, transitivity) b) and computational analysis (scalable annotation)

This enables linguists to directly operationalize their research questions on real corpora, using only prompting rather than model development. This approach suggests a broader shift in computational linguistics: from fixed, pre-defined tasks to user-defined annotation schemes and from model-centric pipelines to prompt-driven analysis. 

In this sense, our NER serves as **a proof of concept** that LLMs can act as general-purpose annotation engines, allowing linguists to explore new questions without engineering overhead.

#P 

# Citations
Dowty, David. 1991. “Thematic Proto-Roles and Argument Selection.” Language 67 (3): 547–619.
Elson, David K., Nicholas Dames, and Kathleen R. McKeown. 2010. “Extracting Social Networks from Literary Fiction.” In Proceedings of the 48th Annual Meeting of the Association for Computational Linguistics, 138–147.
Gildea, Daniel, and Daniel Jurafsky. 2002. “Automatic Labeling of Semantic Roles.” Computational Linguistics 28 (3): 245–288.
Hopper, Paul J., and Sandra A. Thompson. 1980. “Transitivity in Grammar and Discourse.” Language 56 (2): 251–299.
Lambrecht, Knud. 1994. Information Structure and Sentence Form: Topic, Focus, and the Mental Representations of Discourse Referents. Cambridge: Cambridge University Press



  
