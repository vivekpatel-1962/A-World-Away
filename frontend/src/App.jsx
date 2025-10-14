import React, { useState } from 'react';

const requiredManualFeatures = [
  'koi_period', 'koi_duration', 'koi_fpflag_nt', 'koi_fpflag_ss',
  'koi_fpflag_co', 'koi_fpflag_ec', 'koi_depth', 'koi_prad', 'koi_sma',
  'koi_impact', 'koi_ror', 'koi_steff', 'koi_srad', 'koi_smass',
  'koi_slogg', 'koi_smet', 'koi_teq', 'koi_model_snr', 'koi_num_transits'
];

export default function App() {
  const [imageFile, setImageFile] = useState(null);
  const [imagePrediction, setImagePrediction] = useState(null);
  const [manualFeatures, setManualFeatures] = useState(() =>
    requiredManualFeatures.reduce((acc, feat) => ({ ...acc, [feat]: '' }), {})
  );
  const [manualPrediction, setManualPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    setImageFile(e.target.files[0]);
    setImagePrediction(null);
    setManualPrediction(null);
  };

  const submitImage = async () => {
    if (!imageFile) return alert('Please select an image first.');

    const formData = new FormData();
    formData.append('image', imageFile);

    setLoading(true);
    try {
      const response = await fetch('/predict', {
        method: 'POST',
        body: formData,
      });
      const text = await response.text();
      let result;
      try { result = JSON.parse(text); } catch (_) { result = null; }

      if (response.ok && result) {
        setImagePrediction(result);
      } else {
        const msg = (result && result.error) ? result.error : (text || 'Prediction error');
        alert(msg);
      }
    } catch (e) {
      alert('Network error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleManualChange = (e) => {
    const { name, value } = e.target;
    setManualFeatures((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const submitManual = async () => {
    for (const feat of requiredManualFeatures) {
      if (!manualFeatures[feat]) {
        alert(`Please fill in ${feat}`);
        return;
      }
      if (isNaN(Number(manualFeatures[feat]))) {
        alert(`Please enter a valid number for ${feat}`);
        return;
      }
    }

    setLoading(true);
    try {
      const response = await fetch('/predict_manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(manualFeatures),
      });
      const text = await response.text();
      let result;
      try { result = JSON.parse(text); } catch (_) { result = null; }

      if (response.ok && result) {
        setManualPrediction(result);
      } else {
        const msg = (result && result.error) ? result.error : (text || 'Manual prediction error');
        alert(msg);
      }
    } catch (e) {
      alert('Network error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{padding: 20, maxWidth: 600, margin: 'auto'}}>
      <h2>Step 1: Upload Light Curve Image</h2>
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <button onClick={submitImage} disabled={!imageFile || loading} style={{marginLeft: 10}}>
        {loading ? 'Predicting...' : 'Predict Label'}
      </button>

      {imagePrediction && (
        <div style={{marginTop: 20, padding: 10, border: '1px solid #ccc'}}>
          <h3>Image Prediction</h3>
          <p>Label: {imagePrediction.label}</p>
          <p>Confidence: {imagePrediction.confidence_percent ?? imagePrediction.confidence}%</p>

          <h2>Step 2: Enter Manual Data Features</h2>
          <form onSubmit={(e) => {e.preventDefault(); submitManual();}}>
            {requiredManualFeatures.map((feat) => (
              <div key={feat} style={{marginBottom: 10}}>
                <label htmlFor={feat} style={{display: 'block', fontWeight: 'bold'}}>{feat}</label>
                <input
                  type="number"
                  id={feat}
                  name={feat}
                  value={manualFeatures[feat]}
                  onChange={handleManualChange}
                  step="any"
                  required
                  style={{width: '100%', padding: 5}}
                />
              </div>
            ))}
            <button type="submit">Predict with Manual Data</button>
          </form>

          {manualPrediction && (
            <div style={{marginTop: 20}}>
              <h3>Manual Data Prediction</h3>
              <p>Label: {manualPrediction.label}</p>
              <p>Confidence: {manualPrediction.confidence_percent ?? manualPrediction.confidence}%</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
