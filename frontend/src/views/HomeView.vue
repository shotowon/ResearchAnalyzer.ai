<template>
  <transition name="slide-from-top">
    <div class="paper-download" v-if="mounted">
      <form @submit.prevent="submitLink" class="form-container">
        <label for="paper-link">Enter paper link:</label>
        <input
          type="text"
          v-model="paperLink"
          id="paper-link"
          placeholder="https://doi.org/10.1073/pnas.0611500104"
          @keydown.enter="submitLink"
        />
        <button type="submit" class="submit-button">Submit</button>
      </form>
      
      <transition name="fade">
        <p v-if="doi" class="info">Extracted DOI: {{ doi }}</p>
      </transition>
      
      <transition name="fade">
        <p v-if="message" class="info success">Message: {{ message }}</p>
      </transition>
      
      <transition name="fade">
        <p v-if="filePath" class="info">File Path: {{ filePath }}</p>
      </transition>
      
      <transition name="fade">
        <p v-if="error" class="info error">{{ error }}</p>
      </transition>
    </div>
  </transition>
</template>


<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const paperLink = ref("");
    const doi = ref(null);
    const message = ref(null);
    const filePath = ref(null);
    const error = ref(null);
    const mounted = ref(false);

    const extractDOI = (link) => {
      const doiMatch = link.match(/10\.\d{4,9}\/[-._;()/:A-Z0-9]+/i);
      return doiMatch ? doiMatch[0] : null;
    };

    const submitLink = async () => {
      error.value = null;
      message.value = null;
      filePath.value = null;
      const extractedDOI = extractDOI(paperLink.value);

      if (!extractedDOI) {
        error.value = "Invalid link or DOI not found.";
        return;
      }

      doi.value = extractedDOI;

      try {
        const response = await fetch(`http://127.0.0.1:8000/place-pdf?doi=${encodeURIComponent(doi.value)}`, {
          method: "GET",
        });

        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.detail || "Error downloading the PDF");
        }

        message.value = result.message;
        filePath.value = result.file_path;
      } catch (err) {
        error.value = `Error: ${err.message}`;
      }
    };

    onMounted(() => {
      mounted.value = true;
    });

    return {
      paperLink,
      doi,
      message,
      filePath,
      error,
      submitLink,
      mounted
    };
  },
};
</script>


<style scoped>
.paper-download {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  background: #f7f9fc;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
}

input:focus {
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
  outline: none;
}

.submit-button {
  padding: 10px;
  font-size: 1rem;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
}

.submit-button:hover {
  background-color: #0056b3;
}

.submit-button:active {
  transform: scale(0.95);
}

.info {
  margin-top: 10px;
  padding: 10px;
  border-radius: 5px;
  font-size: 1rem;
  transition: opacity 0.3s;
}

.success {
  background-color: #d4edda;
  color: #155724;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.slide-from-top-enter-active {
  transition: transform 0.5s ease, opacity 0.5s ease;
}

.slide-from-top-enter {
  transform: translateY(-50px);
  opacity: 0;
}

.slide-from-top-leave-active {
  transition: transform 0.5s ease, opacity 0.5s ease;
}

.slide-from-top-leave-to {
  transform: translateY(-50px);
  opacity: 0;
}
</style>
