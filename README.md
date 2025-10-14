# 🌌 A-World-Away

This project is an AI/ML-powered portal for the automatic detection of exoplanets using NASA's Kepler, K2, and TESS mission data. It showcases data science, astronomy, and user interactivity through a blend of scientific rigor and accessible machine learning.

---

✨ **Unique Features**

- **Automatic Exoplanet Detection**  
  Uses supervised machine learning to classify objects as confirmed exoplanets, candidates, or false positives.
- **Custom Data Preprocessing**  
  Handles missing values, scales features, and selects variables critical for astronomical classification.
- **Web Interface (Planned)**  
  Will allow users to upload or manually enter new candidate data for real-time prediction.
- **Science-Driven**  
  Integrates domain knowledge (light curves, transits, JWST insights) for interpretable results.

---

🚀 **Features**

- NASA exoplanet dataset ingestion and cleaning  
- Feature engineering for key astrophysical parameters (orbital period, transit duration, planetary radius, etc.)
- Missing data handling (median imputation)
- ML model training with evaluation metrics  
- Label encoding and feature scaling  
- (Planned) Web interface for interactive use  
- Example code and workflow included

---

🛠️ **Technologies Used**

- **Python**: Data handling and ML workflow (mainly via Jupyter Notebook)
- **pandas**: For data manipulation and cleaning
- **scikit-learn**: For preprocessing, model training, and evaluation
- **Jupyter Notebook**: For scientific workflow and demonstration
- **(Planned)**: Web interface for user interaction

---

📖 **How to Use**

1. **Clone the repository.**
2. **Download NASA exoplanet datasets** (Kepler, K2, TESS) and place them in the project directory.
3. **Install requirements**:  
   ```
   pip install pandas scikit-learn jupyter
   ```
4. **Open and run the Jupyter notebook** (`Untitled.ipynb`) to preprocess data, train, and test the model.
5. **(Planned)**: Launch the web interface to upload or enter new candidate data.

---

🔬 **Scientific Background**

- **Transit Method**: Detects exoplanets by observing periodic dips in a star’s brightness as a planet passes in front.
- **JWST Integration**: The James Webb Space Telescope (JWST) observes in infrared, revealing faint, dust-obscured, or distant exoplanets and providing spectra to identify atmospheric gases.
- **Model Features**: Uses astrophysical properties such as orbital period, transit depth, planetary radius, stellar temperature, and false-positive flags to classify candidates.

---

🤝 **Contributing**

Want to make this project better?  
Open an issue or submit a pull request with your suggestions or improvements!

---

📚 **References**

- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/)
- Kepler, K2, and TESS mission data
- JWST science documentation

---

**Happy coding and clear skies!** 🚀🔭
