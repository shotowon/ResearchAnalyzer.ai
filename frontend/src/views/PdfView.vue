<template>
  <div class="pdf-viewer">
    <!-- Use the computed pdfUrl instead of hardcoded PDF file name -->
    <vue-pdf-app style="height: 100vh;" :pdf="pdfUrl" @error="handleError" ></vue-pdf-app>

    <!-- Show loading or error message if needed -->
    <div v-if="error" class="error">{{ error }}</div>
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

    const pdfUrl = computed(() => {
      return `http://127.0.0.1:8000/file/${encodeURIComponent(props.filePath)}`;
    });

    const handleError = (err) => {
      console.error('PDF loading error:', err);
      error.value = 'Failed to load PDF. Please try again.';
    };

   

    onMounted(() => {
      error.value = null;
    });

    return {
      error,
      pdfUrl,
      handleError,
      
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
</style>
