# Data

## `raw/SR2025.csv`: City of Toronto 311 open data (not in git)
- Source: [311 Service Requests – Customer Initiated](https://open.toronto.ca/dataset/311-service-requests-customer-initiated/), City of Toronto Open Data, 2025 file. Licence: Open Government Licence – Toronto.
- Download with `python -m agent311.data` (~7 MB zip, 75 MB CSV, 500,269 rows).
- Columns: `Creation Date`, `Status`, `First 3 Chars of Postal Code` (or the word "Intersection"), `Intersection Street 1`, `Intersection Street 2`, `Ward`, `Service Request Type` (539 distinct), `Division`, `Section`.
- **Not included in the City's data:** the resident's description of the problem, and the date the request was closed.

## `messages/`: resident messages (synthetic)
Because the open data has no free text, these messages were **written for this project** (by Claude, during development) to look like what residents might type.
- `train.csv`: 160 messages, 10 per class (15 request types + `OTHER`).
- `test.csv`: 96 messages, 6 per class, one per writing style: `plain`, `short`, `typos`, `second_language`, `emotional`, `indirect`. Written separately from the training messages.

**Limitation:** same author for train and test, and not real residents. Add your own messages to `test.csv` (same columns) to get a more honest score.

## `city_info/`: knowledge base (demo content)
20 short articles written for this project. General guidance, **not official City policy**. See `city_info/README.md`.
