document.addEventListener("DOMContentLoaded", function() {
  const csrftoken = getCookie("csrftoken");

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  async function postAndUpdate(fieldName, extraFields = []) {
  const payload = new FormData();
  // Always include the changed field
  payload.append(fieldName, document.getElementById(fieldName).value);

  // Include dependent fields explicitly
  extraFields.forEach(dep => {
    const el = document.getElementById(dep);
    if (el) {
      payload.append(dep, el.value || el.textContent);
    }
  });

  const response = await fetch("/diode/calculate/", {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    body: payload
  });

  const result = await response.json();
  console.log("Response for", fieldName, result);

  for (const key in result) {
    const el = document.getElementById(key);
    if (el) {
      let val = result[key]; // backend already provides correct units/format
      if ("value" in el) el.value = val;
      else el.textContent = val;
    }
  }
}

// --- Dependency mapping for blur events ---
const dependencyMap = {    
  ni: ["Vbi"],   // when ni changes, backend computes Vbi
  Vapp: ["Wn"],  // when Vapp changes, backend computes Wn
  Wn: ["Wp"],    // when Wn changes, backend computes Wp
  Is: ["Id"],    // when Is changes, backend computes Id
};

Object.keys(dependencyMap).forEach(sourceId => {
  const input = document.getElementById(sourceId);
  if (input) {
    input.addEventListener("blur", () => {
      postAndUpdate(sourceId, dependencyMap[sourceId]);
    });
  }
});


  // --- Device selector ---
  const deviceSelect = document.getElementById("deviceSelect");
  if (deviceSelect) {
    deviceSelect.addEventListener("change", function() {
      window.location.href = `/diode/?diode=${this.value}`;
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const vappSelect = document.getElementById("Vapp");
  const Vmin = -1.0, Vmax = 1.0, step = 0.05;

  for (let v = Vmin; v <= Vmax + 1e-9; v += step) {
    const opt = document.createElement("option");
    opt.value = v.toFixed(2);
    opt.textContent = v.toFixed(2) + " V";
    vappSelect.appendChild(opt);
  }

  // Start at 0 V, keep enabled for tabbing but lock arrow keys
  vappSelect.value = "0.00";
  vappSelect.dataset.locked = "true";  // custom flag
});

document.getElementById("Ileak").addEventListener("blur", () => {
  const ileakField = document.getElementById("Ileak");
  if (ileakField && ileakField.value.trim() !== "") {
    const vappSelect = document.getElementById("Vapp");
    vappSelect.dataset.locked = "false";   // unlock arrow keys
    vappSelect.focus();                    // move focus to Vapp
  }
});


const vappSelect = document.getElementById("Vapp");
vappSelect.addEventListener("keydown", (event) => {
  event.preventDefault(); // stop default popup behavior

  if (event.key === "ArrowUp") {
    if (vappSelect.selectedIndex < vappSelect.options.length - 1) {
      vappSelect.selectedIndex++;
      postAndUpdate("Vapp");
    }
  } else if (event.key === "ArrowDown") {
    if (vappSelect.selectedIndex > 0) {
      vappSelect.selectedIndex--;
      postAndUpdate("Vapp");
    }
  }
});




