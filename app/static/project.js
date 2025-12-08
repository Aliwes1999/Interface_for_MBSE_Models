// Global flag to ensure event delegation is only set up once
let eventListenersAttached = false;

// Global function to attach event listeners - can be called multiple times
function attachEventListeners() {
  console.log("Attaching event listeners...");

  // Only attach delegated event listeners once
  if (!eventListenersAttached) {
    // Version selector change event - use event delegation
    document.addEventListener("change", function (e) {
      if (e.target.classList.contains("version-selector")) {
        const reqId = e.target.getAttribute("data-req-id");
        const versionIndex = e.target.value;
        updateRowWithVersionData(reqId, versionIndex);
      }
    });

    // Edit requirement button click - use event delegation
    document.addEventListener("click", function (e) {
      if (
        e.target.classList.contains("edit-requirement-btn") ||
        e.target.closest(".edit-requirement-btn")
      ) {
        const button = e.target.classList.contains("edit-requirement-btn")
          ? e.target
          : e.target.closest(".edit-requirement-btn");

        if (button && !button.disabled) {
          const reqId = button.getAttribute("data-req-id");
          const versionId = button.getAttribute("data-version-id");
          openEditModal(reqId, versionId);
        }
      }
    });

    eventListenersAttached = true;
  }

  // Edit form submission
  const editForm = document.getElementById("editRequirementForm");
  if (editForm && !editForm.dataset.listenerAttached) {
    editForm.addEventListener("submit", function (e) {
      const versionId = document.getElementById("editVersionId").value;
      this.action = `/requirement_version/${versionId}/update`;
    });
    editForm.dataset.listenerAttached = "true";
  }

  // Apply filters button
  const applyBtn = document.getElementById("applyFilters");
  if (applyBtn && !applyBtn.dataset.listenerAttached) {
    applyBtn.addEventListener("click", applyFilters);
    applyBtn.dataset.listenerAttached = "true";
  }

  // Reset filters button
  const resetBtn = document.getElementById("resetFilters");
  if (resetBtn && !resetBtn.dataset.listenerAttached) {
    resetBtn.addEventListener("click", function () {
      document.getElementById("filterText").value = "";
      document.getElementById("filterStatus").value = "";
      document.getElementById("filterCategory").value = "";
      document.querySelectorAll("[data-filter-column]").forEach((select) => {
        select.value = "";
      });
      applyFilters();
    });
    resetBtn.dataset.listenerAttached = "true";
  }

  // Filter on Enter
  const filterText = document.getElementById("filterText");
  if (filterText && !filterText.dataset.listenerAttached) {
    filterText.addEventListener("keyup", function (e) {
      if (e.key === "Enter") {
        applyFilters();
      }
    });
    filterText.dataset.listenerAttached = "true";
  }

  console.log("Event listeners attached");
}

// Global function to update custom columns
function updateCustomColumns(newColumns) {
  console.log("Updating custom columns:", newColumns);
  window.PROJECT_CUSTOM_COLUMNS = newColumns;
  // Reinitialize filters with new columns
  initializeFilters();
}

// Functions
function updateRowWithVersionData(reqId, versionIndex) {
  const row = document.getElementById(`req-row-${reqId}`);
  const versionsData = document.getElementById(`versions-data-${reqId}`);
  const versionElements = versionsData.querySelectorAll(".version-data");

  let selectedVersion = null;
  versionElements.forEach((el) => {
    if (el.getAttribute("data-version-index") === versionIndex) {
      selectedVersion = el;
    }
  });

  if (selectedVersion) {
    const versionId = selectedVersion.getAttribute("data-version-id");

    // Update custom data cells
    let customData = {};
    try {
      const customDataStr = selectedVersion.getAttribute("data-custom-data");
      if (customDataStr && customDataStr.trim() !== "") {
        customData = JSON.parse(customDataStr);
      }
    } catch (e) {
      console.error("Error parsing custom data:", e);
      customData = {};
    }

    const customDataCells = row.querySelectorAll(".custom-data-cell");
    customDataCells.forEach((cell) => {
      const column = cell.getAttribute("data-column");
      cell.textContent = customData[column] || "–";
    });

    // Update status cell with hex color
    const statusCell = row.querySelector(".status-cell");
    const status = selectedVersion.getAttribute("data-status");
    const statusColor = selectedVersion.getAttribute("data-status-color");
    statusCell.innerHTML = `<span class="badge" style="background-color: ${statusColor}">${status}</span>`;

    // Update user cell if exists
    const userCell = row.querySelector(".user-cell");
    if (userCell) {
      // Keep the user cell as is, or you could update it based on version creator
      // For now, we'll leave it unchanged as it shows the creator
    }

    const editButton = row.querySelector(".edit-requirement-btn");
    if (editButton) {
      editButton.setAttribute("data-version-id", versionId);
    }

    const deleteForm = row.querySelector(".delete-version-form");
    if (deleteForm) {
      deleteForm.action = `/requirement_version/${versionId}/delete`;
    }
  }
}

function initializeFilters() {
  console.log("Initializing filters...");

  // Populate category filter
  const categories = new Set();
  document.querySelectorAll(".category-cell").forEach((cell) => {
    const category = cell.textContent.trim();
    if (category && category !== "–") {
      categories.add(category);
    }
  });

  const categoryFilter = document.getElementById("filterCategory");
  if (categoryFilter) {
    // Clear existing options except the first "Alle" option
    while (categoryFilter.options.length > 1) {
      categoryFilter.remove(1);
    }

    categories.forEach((category) => {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categoryFilter.appendChild(option);
    });
  }

  // Create dynamic column filters
  const customColumns = window.PROJECT_CUSTOM_COLUMNS || [];
  const dynamicFiltersContainer = document.getElementById(
    "dynamicFiltersContainer"
  );

  if (dynamicFiltersContainer) {
    // Clear existing dynamic filters
    dynamicFiltersContainer.innerHTML = "";

    customColumns.forEach((column) => {
      const values = new Set();
      document
        .querySelectorAll(`.custom-data-cell[data-column="${column}"]`)
        .forEach((cell) => {
          const value = cell.textContent.trim();
          if (value && value !== "–") {
            values.add(value);
          }
        });

      if (values.size > 0) {
        const filterDiv = document.createElement("div");
        filterDiv.className = "mb-2";

        const label = document.createElement("label");
        label.className = "form-label fw-bold";
        label.textContent = column;

        const select = document.createElement("select");
        select.className = "form-select";
        select.setAttribute("data-filter-column", column);

        const allOption = document.createElement("option");
        allOption.value = "";
        allOption.textContent = "Alle";
        select.appendChild(allOption);

        values.forEach((value) => {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = value;
          select.appendChild(option);
        });

        filterDiv.appendChild(label);
        filterDiv.appendChild(select);
        dynamicFiltersContainer.appendChild(filterDiv);
      }
    });
  }

  console.log("Filters initialized");
}

function applyFilters() {
  console.log("Applying filters...");

  const textFilter = document.getElementById("filterText").value.toLowerCase();
  const statusFilter = document.getElementById("filterStatus").value;
  const categoryFilter = document.getElementById("filterCategory").value;

  const dynamicFilters = {};
  document.querySelectorAll("[data-filter-column]").forEach((select) => {
    const column = select.getAttribute("data-filter-column");
    const value = select.value;
    if (value) {
      dynamicFilters[column] = value;
    }
  });

  let visibleCount = 0;
  let totalCount = 0;

  document.querySelectorAll("tbody tr[data-req-id]").forEach((row) => {
    totalCount++;
    let visible = true;

    if (textFilter) {
      const title = row.querySelector(".title-cell").textContent.toLowerCase();
      const description = row
        .querySelector(".description-cell")
        .textContent.toLowerCase();
      if (!title.includes(textFilter) && !description.includes(textFilter)) {
        visible = false;
      }
    }

    if (statusFilter && visible) {
      const status = row.querySelector(".status-cell").textContent.trim();
      if (status !== statusFilter) {
        visible = false;
      }
    }

    if (categoryFilter && visible) {
      const category = row.querySelector(".category-cell").textContent.trim();
      if (category !== categoryFilter) {
        visible = false;
      }
    }

    if (visible && Object.keys(dynamicFilters).length > 0) {
      for (const [column, value] of Object.entries(dynamicFilters)) {
        const cell = row.querySelector(
          `.custom-data-cell[data-column="${column}"]`
        );
        if (cell) {
          const cellValue = cell.textContent.trim();
          if (cellValue !== value) {
            visible = false;
            break;
          }
        }
      }
    }

    if (visible) {
      row.style.display = "";
      visibleCount++;
    } else {
      row.style.display = "none";
    }
  });

  const resultText = `${visibleCount} von ${totalCount} angezeigt`;
  const resultCount = document.getElementById("filterResultCount");
  if (resultCount) {
    resultCount.textContent = resultText;
  }

  console.log(`Filter applied: ${visibleCount}/${totalCount} visible`);
}

function openEditModal(reqId, versionId) {
  console.log("Opening edit modal for req:", reqId, "version:", versionId);

  document.getElementById("editVersionId").value = versionId;

  const versionsData = document.getElementById(`versions-data-${reqId}`);
  const versionElements = versionsData.querySelectorAll(".version-data");

  let selectedVersion = null;
  versionElements.forEach((el) => {
    if (el.getAttribute("data-version-id") === versionId) {
      selectedVersion = el;
    }
  });

  if (selectedVersion) {
    document.getElementById("editTitle").value =
      selectedVersion.getAttribute("data-title");
    document.getElementById("editDescription").value =
      selectedVersion.getAttribute("data-description");
    document.getElementById("editCategory").value =
      selectedVersion.getAttribute("data-category");

    let customData = {};
    try {
      const customDataStr = selectedVersion.getAttribute("data-custom-data");
      console.log("Raw custom data string:", customDataStr);

      if (
        customDataStr &&
        customDataStr.trim() !== "" &&
        customDataStr !== "null"
      ) {
        customData = JSON.parse(customDataStr);
        console.log("Parsed custom data:", customData);
      }
    } catch (e) {
      console.error("Error parsing custom data in edit modal:", e);
      console.error(
        "Problematic string was:",
        selectedVersion.getAttribute("data-custom-data")
      );
      customData = {};
    }

    const dynamicContainer = document.getElementById("dynamicColumnsContainer");
    dynamicContainer.innerHTML = "";

    // USE GLOBAL VARIABLE INSTEAD OF JINJA2
    const customColumns = window.PROJECT_CUSTOM_COLUMNS || [];
    console.log("Custom columns for edit:", customColumns);
    console.log("Custom data object:", customData);

    customColumns.forEach((column) => {
      const fieldDiv = document.createElement("div");
      fieldDiv.className = "mb-3";

      const label = document.createElement("label");
      label.className = "form-label";
      label.textContent = column;

      const input = document.createElement("input");
      input.type = "text";
      input.className = "form-control";
      input.name = `custom_${column}`;
      input.value = customData[column] || "";

      fieldDiv.appendChild(label);
      fieldDiv.appendChild(input);
      dynamicContainer.appendChild(fieldDiv);
    });

    const modal = new bootstrap.Modal(
      document.getElementById("editRequirementModal")
    );
    modal.show();
  }
}

// Initialize on DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
  console.log("Project.js loaded");
  console.log("Custom columns:", window.PROJECT_CUSTOM_COLUMNS);

  // Attach event listeners
  attachEventListeners();

  // Initialize filters
  initializeFilters();
});
