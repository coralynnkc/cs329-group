Here, we made the model yield probabilistic classification for E, C, and N labels for hypotheses.

Where upon, we first merge by the same `item_id`, then consider all E, C, N together row-wise, and simply output average probabilities per sub-column, that is, for all gold label Es grouped together, what is average probablitiy of items under it with E, with N, with C, and so on, again for gold label of Ns and Cs. We call this the centroid of the simplex.

Note that in the results JSON, a larger percentage (probability) of the time, in many cases, the model (Sonnet 4.6) does correctly guess the accurate label, except for deviating a few, and the deviation to exactly which label is also commensurated via the other two probabilities here, bringing exactness in the scenario, but giving the model some leeway instead of crude binary validation of match/mismatch.

Then iterate it folder-wise as there are languages of "de", "vi", "fr", "ru", "hi", and "en".

