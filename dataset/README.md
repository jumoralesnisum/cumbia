# Dataset extraction and transformations
Link: https://www.kaggle.com/datasets/sebastienverpile/consumercomplaintsdata

Steps:
## Extract:
Download and unzip dataset from kaggle. Run 
<code>1_extract.py</code>.

## Translate
Run <code>2_translate_simple.py</code>

This procedure might fail halfway since the translation service has a daily quota.
If the process fail, run <code>3_delta.py</code> and then run <code>2_translate_simple.py</code> again

## Add to the result
Run <code>3_delta.py</code> to take the translated increments into the result

With the resulting translated dataset we only needed some data formatting tweaks to be ready to use it in the GCP Vertex AI models