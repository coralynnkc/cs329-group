## Agency-Based Named Entity Recognition in Narrative Texts

  # Task Description
  We introduce an extension of Named Entity Recognition (NER) that captures  not only which entities are mentioned in a text, but the **role they play in driving events** i.e. subject-object relations.
Specifically, we define an NER task that distinguishes between entities that actively participate in events and those that are passively referenced. Our labels are stratified based on activeness, as well as type of verb, and realtion to direct subject.
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

thematic roles (agent, patient, experiencer)
transitivity and argument structure
voice alternations (active vs passive constructions)

  
