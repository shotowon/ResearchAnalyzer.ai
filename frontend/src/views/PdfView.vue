<template>
  <div class="pdf-viewer">
    <vue-pdf-app style="height: 100vh;" :pdf="pdfUrl" @error="handleError"></vue-pdf-app>

    <!-- Show loading or error message if needed -->
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Button to summarize PDF, disabled after one press -->
    <button @click="summarizePdf" :disabled="loading || buttonPressed">
      {{ loading ? 'Summarizing...' : 'Summarize PDF' }}
    </button>

    <!-- Display the summary -->
    <div v-if="summary" class="summary">
      <h2>Summary:</h2>
      <p>{{ summary }}</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import VuePdfApp from 'vue3-pdf-app';

export default {
  name: 'PdfView',
  components: {
    VuePdfApp,
  },
  props: {
    filePath: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const error = ref(null);
    const summary = ref(null);
    const loading = ref(false);
    const buttonPressed = ref(false);

    const pdfUrl = computed(() => {
      return `http://127.0.0.1:8000/file/${encodeURIComponent(props.filePath)}`;
    });

    const handleError = (err) => {
      console.error('PDF loading error:', err);
      error.value = 'Failed to load PDF. Please try again.';
    };

    const summarizePdf = async () => {
      console.log("Summarize PDF button clicked");
      loading.value = true;
      error.value = null;
      summary.value = null;
      buttonPressed.value = true;

      try {
        const response = await fetch(`http://127.0.0.1:8000/summarize/${encodeURIComponent(props.filePath)}`);
        console.log("Response status:", response.status);
        if (!response.ok) {
          throw new Error('Failed to summarize PDF.');
        }

        // Start polling after initiating the summarization
        pollSummary();
      } catch (err) {
        console.error('Error fetching summary:', err);
        error.value = 'Failed to summarize PDF. Please try again.';
        loading.value = false;
        buttonPressed.value = false;
      }
    };

    const pollSummary = async () => {
      const fileName = props.filePath.split('/').pop();
      try {
        const summaryResponse = await fetch(`http://127.0.0.1:8000/summary/${encodeURIComponent(fileName)}`);
        if (summaryResponse.ok) {
          const summaryData = await summaryResponse.json();
          if (summaryData.status === "completed") {
            summary.value = summaryData.summary;
            loading.value = false;
          } else {
            setTimeout(pollSummary, 2000); // Poll again in 2 seconds
          }
        }
      } catch (err) {
        console.error('Error polling summary:', err);
        error.value = 'Failed to retrieve summary. Please try again later.';
        loading.value = false;
        buttonPressed.value = false;
      }
    };

    onMounted(() => {
      error.value = null;
      buttonPressed.value = localStorage.getItem('buttonPressed') === 'false';
      summary.value = localStorage.getItem('summary') || null;
    });

    return {
      error,
      pdfUrl,
      handleError,
      summarizePdf,
      summary,
      loading,
      buttonPressed,
    };
  },
};
</script>

<style scoped>
.pdf-viewer {
  position: relative;
  height: 100vh;
}

.loading, .error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2rem;
  color: #666;
}

.error {
  color: #ff4444;
}

.summary {
  margin-top: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
}
</style>
