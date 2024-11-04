<template>
  <div class="pdf-viewer">
    <vue-pdf-app style="height: 100vh;" :pdf="pdfUrl" @error="handleError"></vue-pdf-app>

    <transition name="fade">
      <div v-if="error" class="error">{{ error }}</div>
    </transition>

    <transition name="fade">
      <button @click="summarizePdf" :disabled="loading || buttonPressed" class="summarize-button">
        {{ loading ? 'Summarizing...' : 'Summarize PDF' }}
      </button>
    </transition>

    <transition name="slide-up">
      <div v-if="summary" class="summary" v-html="renderedSummary"></div>
    </transition>
  </div>
</template>


<script>
import { ref, computed } from 'vue';
import VuePdfApp from 'vue3-pdf-app';
import { marked } from 'marked';

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

    const pdfUrl = computed(() => `http://127.0.0.1:8000/file/${encodeURIComponent(props.filePath)}`);

    const renderedSummary = computed(() => marked(summary.value || ''));

    const handleError = (err) => {
      console.error('PDF loading error:', err);
      error.value = 'Failed to load PDF. Please try again.';
    };

    const summarizePdf = async () => {
      loading.value = true;
      error.value = null;
      summary.value = null;
      buttonPressed.value = true;

      try {
        const response = await fetch(`http://127.0.0.1:8000/summarize/${encodeURIComponent(props.filePath)}`);
        if (!response.ok) throw new Error('Failed to summarize PDF.');

        pollSummary();
      } catch (err) {
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
            setTimeout(pollSummary, 2000);
          }
        }
      } catch (err) {
        error.value = 'Failed to retrieve summary. Please try again later.';
        loading.value = false;
        buttonPressed.value = false;
      }
    };

    return {
      error,
      pdfUrl,
      handleError,
      summarizePdf,
      summary,
      loading,
      buttonPressed,
      renderedSummary,
    };
  },
};
</script><style scoped>
.pdf-viewer {
  position: relative;
  height: 100vh;
  padding: 20px;
  background-color: #1e1e2f; /* Dark background */
  font-family: 'Arial', sans-serif;
  color: #e6e6e6; /* Light text for contrast */
}

.loading, .error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2rem;
  text-align: center;
  color: #ff4444;
  padding: 20px;
  border-radius: 10px;
  background-color: #2e2e38; /* Slightly lighter dark background */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.summarize-button {
  display: block;
  margin: 20px auto;
  padding: 10px 20px;
  font-size: 1.2rem;
  color: white;
  background-color: #007bff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
}

.summarize-button:hover {
  background-color: #0056b3;
}

.summarize-button:disabled {
  background-color: #b0c4de;
  cursor: not-allowed;
}

.summary {
  margin-top: 30px;
  padding: 20px;
  background-color: #2e2e38; /* Darker card background */
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  animation: fade-in 0.5s ease-in;
  line-height: 1.6;
  color: #e6e6e6; /* Light text for contrast */
}

.summary h1, .summary h2, .summary h3 {
  margin-top: 1em;
  color: #d4d4d4; /* Slightly lighter text for headers */
}

.summary p {
  font-size: 1rem;
  color: #e6e6e6;
}

.summary ul, .summary ol {
  padding-left: 1.5rem;
  color: #cfcfcf; /* Lists have a slightly different shade */
}

.summary code {
  background-color: #3e3e48; /* Dark code background */
  color: #ffcc99; /* Light code text */
  padding: 2px 4px;
  border-radius: 3px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease-in-out;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.bounce-enter-active, .bounce-leave-active {
  transition: transform 0.5s ease-in-out;
}

.bounce-enter, .bounce-leave-to {
  transform: scale(0.8);
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.5s ease-in-out, opacity 0.5s ease-in-out;
}

.slide-up-enter, .slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>
