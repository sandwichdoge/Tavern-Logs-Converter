## WIP

### Convert all Tavern logs into usable axolotl dataset formats.

#### Features:

- Integrate character's description by parsing character cards.
- Fuzzy obfuscation of user's name.
- Support axolotl-friendly prompt formats.

#### TODO:

- Obfuscate character's name to prevent overfitting.
- Fuzzy system prompt generator to prevent overfitting.
- Custom prompt formats.

#### How to use:
```
pip3 install -r requirements.txt
python3 main.py  -i /path/to/SillyTavern -f sharegpt
```