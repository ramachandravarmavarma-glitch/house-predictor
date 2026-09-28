/**
 * static/js/prediction.js
 * Multi-stage inference interaction and dynamic results rendering for EstateAI
 */

const PRESETS = {
  bangalore: {
    location: 'Whitefield, Bangalore',
    area: 1850,
    bedrooms: 3,
    bathrooms: 2,
    floors: 2,
    parking: 1,
    furnishing_status: 'Semi-Furnished',
    main_road: 'yes',
    air_conditioning: 'yes',
    guestroom: 'no',
    basement: 'no',
    preferred_area: 'yes'
  },
  mumbai: {
    location: 'Bandra West, Mumbai',
    area: 2600,
    bedrooms: 4,
    bathrooms: 3,
    floors: 2,
    parking: 2,
    furnishing_status: 'Furnished',
    main_road: 'yes',
    air_conditioning: 'yes',
    guestroom: 'yes',
    basement: 'no',
    preferred_area: 'yes'
  },
  pune: {
    location: 'Kothrud, Pune',
    area: 1250,
    bedrooms: 2,
    bathrooms: 2,
    floors: 1,
    parking: 1,
    furnishing_status: 'Semi-Furnished',
    main_road: 'yes',
    air_conditioning: 'no',
    guestroom: 'no',
    basement: 'no',
    preferred_area: 'no'
  }
};

function loadPreset(type) {
  const p = PRESETS[type];
  if (!p) return;

  const form = document.getElementById('predictionForm');
  for (const [key, val] of Object.entries(p)) {
    const el = form.elements[key];
    if (el) {
      el.value = val;
    }
  }

  showNotification(`Loaded ${type.charAt(0).toUpperCase() + type.slice(1)} sample profile`, 'info');
}

function handlePredictionSubmit(e) {
  e.preventDefault();

  const form = document.getElementById('predictionForm');
  const loader = document.getElementById('estimationLoader');
  const stageText = document.getElementById('loaderStageText');
  const subtext = document.getElementById('loaderSubtext');
  const resultCard = document.getElementById('resultCardContainer');

  // Collect data
  const formData = new FormData(form);
  const payload = {};
  formData.forEach((value, key) => {
    payload[key] = value;
  });

  // Client-side quick validation
  const area = parseFloat(payload.area);
  if (isNaN(area) || area < 500) {
    showNotification('Please enter a valid area of at least 500 sq ft', 'danger');
    return;
  }

  if (!payload.location) {
    showNotification('Please select a valid property location', 'danger');
    return;
  }

  // Switch UI to Multi-Stage Loading
  form.style.display = 'none';
  resultCard.style.display = 'none';
  loader.style.display = 'block';

  stageText.innerText = "Analyzing property characteristics...";
  subtext.innerText = "Encoding features and normalizing numerical dimensions";

  // Stage 1 delay -> Stage 2
  setTimeout(() => {
    stageText.innerText = "Generating estimate...";
    subtext.innerText = "Computing matrix dot-product with fitted Linear Regression weights";

    // Call real inference API
    fetch('/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
      .then(response => response.json())
      .then(res => {
        setTimeout(() => {
          loader.style.display = 'none';

          if (!res.success) {
            form.style.display = 'block';
            showNotification(res.error || 'Prediction calculation failed.', 'danger');
            return;
          }

          displayPredictionResult(res.prediction);
        }, 500);
      })
      .catch(err => {
        loader.style.display = 'none';
        form.style.display = 'block';
        showNotification('Network or server error during valuation. Please try again.', 'danger');
      });
  }, 750);
}

function displayPredictionResult(pred) {
  const resultContainer = document.getElementById('resultCardContainer');

  document.getElementById('resPriceMain').innerText = pred.formatted_price;
  document.getElementById('resPriceWords').innerText = `(${pred.price_in_words})`;
  document.getElementById('resValuationBand').innerText = `${pred.valuation_low} - ${pred.valuation_high}`;
  document.getElementById('resRateSqft').innerText = `${pred.price_per_sqft} / sq ft`;
  document.getElementById('resModelUsed').innerText = pred.model_used;
  document.getElementById('resModelR2').innerText = pred.model_r2;
  document.getElementById('resTimestamp').innerText = pred.created_at || 'Just now';

  // Render input summary chips
  const chipsContainer = document.getElementById('resSummaryChips');
  const d = pred.input_summary;
  chipsContainer.innerHTML = `
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">Location</span>
      <strong>${d.location}</strong>
    </div>
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">Area</span>
      <strong>${d.area} sq ft</strong>
    </div>
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">Bedrooms</span>
      <strong>${d.bedrooms} BHK</strong>
    </div>
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">Bathrooms</span>
      <strong>${d.bathrooms} Bath</strong>
    </div>
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">Floors</span>
      <strong>${d.floors}</strong>
    </div>
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">Parking</span>
      <strong>${d.parking} Spaces</strong>
    </div>
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">Furnishing</span>
      <strong>${d.furnishing_status}</strong>
    </div>
    <div style="background: rgba(255,255,255,0.03); padding:0.6rem; border-radius:6px;">
      <span style="color:var(--text-muted); display:block; font-size:0.72rem;">A/C & Prime</span>
      <strong>A/C: ${d.air_conditioning}, Prime: ${d.preferred_area}</strong>
    </div>
  `;

  resultContainer.style.display = 'block';
  resultContainer.scrollIntoView({ behavior: 'smooth' });
}

function resetFormForNewEstimate() {
  const form = document.getElementById('predictionForm');
  const resultCard = document.getElementById('resultCardContainer');
  resultCard.style.display = 'none';
  form.style.display = 'block';
  form.scrollIntoView({ behavior: 'smooth' });
}
