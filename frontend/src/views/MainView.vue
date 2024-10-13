<template>
  <div class="paper-download">
    <form @submit.prevent="submitLink">
      <label for="paper-link">Enter paper link:</label>
      <input
        type="text"
        v-model="paperLink"
        id="paper-link"
        placeholder="https://doi.org/10.1073/pnas.0611500104"
        @keydown.enter="submitLink"
      />
      <button type="submit">Submit</button>
    </form>
    <p v-if="doi">Extracted DOI: {{ doi }}</p>
    <p v-if="message">Message: {{ message }}</p>
    <p v-if="filePath">File Path: {{ filePath }}</p>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
    const paperLink = ref("");
    const doi = ref(null);
    const message = ref(null);
    const filePath = ref(null);
    const error = ref(null);

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

    return {
      paperLink,
      doi,
      message,
      filePath,
      error,
      submitLink,
    };
  },
};
</script>

<style scoped>
.paper-download {
  max-width: 400px;
  margin: auto;
}

input {
  width: 100%;
  padding: 8px;
  margin: 10px 0;
}

button {
  padding: 8px 16px;
}

.error {
  color: red;
}
</style>
