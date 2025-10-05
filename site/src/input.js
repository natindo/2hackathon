
class DynamicForm {
  constructor() {
    this.inputContainer = document.getElementById('input-container');
    this.formPreview = document.getElementById('form-preview');
    this.clearBtn = document.getElementById('clear-all');
    this.inputCount = 0;

    this.init();
  }

  init() {
    // Start with 2 input fields
    this.addInputField();
    this.addInputField();

    // Add event listeners
    this.inputContainer.addEventListener('keydown', (e) => {
      if (e.target.type === 'text') {
        this.handleKeyDown(e.target, e);
      }
    });

    this.inputContainer.addEventListener('input', (e) => {
      if (e.target.type === 'text') {
        this.updatePreview();
      }
    });

    this.clearBtn.addEventListener('click', () => {
      this.clearAllFields();
    });

    // Initial preview update
    this.updatePreview();
  }

  addInputField() {
    this.inputCount++;
    const inputId = `input-${this.inputCount}`;

    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group new-input';
    inputGroup.innerHTML = `
            <label for="${inputId}">Место ${this.inputCount}</label>
            <input type="text" 
                   id="${inputId}" 
                   placeholder="Место ${this.inputCount}">
        `;

    this.inputContainer.appendChild(inputGroup);

    // Remove animation class after animation completes
    setTimeout(() => {
      inputGroup.classList.remove('new-input');
    }, 300);

    return inputId;
  }

  handleKeyDown(inputElement, event) {
    const allInputs = this.getAllInputs();
    const lastInput = allInputs[allInputs.length - 1];

    // Only handle Tab or Enter on the last input that has content
    if (inputElement === lastInput && inputElement.value.trim() !== '') {
      if (event.key === 'Tab' || event.key === 'Enter') {
        event.preventDefault(); // Prevent default Tab behavior

        const newInputId = this.addInputField();

        // Focus the new input after a short delay
        setTimeout(() => {
          document.getElementById(newInputId).focus();
        }, 50);
      }
    }
  }

  getAllInputs() {
    return Array.from(this.inputContainer.querySelectorAll('input[type="text"]'));
  }

  getFormData() {
    const data = {};
    this.getAllInputs().forEach((input, index) => {
      if (input.value.trim() !== '') {
        data[`field${index + 1}`] = input.value;
      }
    });
    return data;
  }

  updatePreview() {
    const formData = this.getFormData();

    if (Object.keys(formData).length === 0) {
      this.formPreview.textContent = 'No data entered yet.';
    } else {
      this.formPreview.textContent = JSON.stringify(formData, null, 2);
    }
  }

  clearAllFields() {
    this.inputContainer.innerHTML = '';
    this.inputCount = 0;

    // Add back the initial 2 fields
    this.addInputField();
    this.addInputField();
    this.updatePreview();

  }
}

// Initialize the dynamic form when the page loads
document.addEventListener('DOMContentLoaded', () => {
  window.dynamicForm = new DynamicForm();
});