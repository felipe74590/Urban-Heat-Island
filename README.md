# Urban-Heat-Island
Studying urban heat island effect in Austin, Texas using Google Earth Engine.

To run main.py run ```uv run main.py -c``` in your terminal. This will prompt you enter a city name to generate a heat map for that urban center. To run the default map, run ```uv run main.py```, this will map the urban heat island of Austin, Texas as a default.

To create Heat Map dashboard in streamlit run ```uv run streamlit run src/app.py```

## Running GOOGLE Earth Engine
Using google earth engine requires an gmail, install ```geemap``` then, run this command in your virtual environment ```earthengine authenticate```. It will require you to follow the authentication process.
Once data is collected and stored, this should not be needed unless new data is needed.

![image](https://github.com/user-attachments/assets/c9b89b58-2c9f-4558-8749-39e1de901f76)
