<template>
  <div class="file-manager">
    <h2>Uploaded Files</h2>
    <transition-group name="slide-fade" tag="ul">
      <router-link
        v-for="file in files"
        :key="file.name"
        :to="`/files/${encodeURIComponent(file.name)}`"
        target="_blank"
        class="file-link"
      >
        <li>{{ file.name }}</li>
      </router-link>
    </transition-group>
    <transition name="fade">
      <p v-if="files.length === 0">No files uploaded yet.</p>
    </transition>
    <transition name="fade">
      <p v-if="error" class="error">{{ error }}</p>
    </transition>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const files = ref([]);
    const error = ref(null);

    const fetchFiles = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/files');
        const result = await response.json();
        if (result.status_code !== 200) {
          throw new Error(result.detail || 'Error fetching files');
        }
        files.value = result.files;
      } catch (err) {
        error.value = `Error: ${err.message}`;
      }
    };

    onMounted(() => {
      fetchFiles();
    });

    return {
      files,
      error,
    };
  },
};
</script>

<style scoped>
.file-manager {
  position: fixed;
  top: 10%;
  left: 2%;
  max-width: 350px;
  padding: 20px;
  background-color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-family: 'Arial', sans-serif;
  overflow-y: auto;
  max-height: 80%;
  text-align: center;
  animation: slide-in-left 0.5s ease-in-out;
}

h2 {
  color: #333;
  font-size: 1.8rem;
  margin-bottom: 20px;
  text-align: center;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.file-link {
  display: block;
  text-decoration: none;
  margin: 10px 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 8px;
  transition: background-color 0.3s ease, transform 0.2s;
}

.file-link:hover {
  background-color: #e8f0fe;
  transform: translateX(5px);
}

.file-link li {
  font-size: 1rem;
  font-weight: 500;
}

.error {
  color: red;
  font-size: 1.1rem;
  margin-top: 10px;
}

p {
  font-size: 1rem;
  color: #666;
}

@keyframes slide-in-left {
  from {
    opacity: 0;
    transform: translateX(-100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.5s ease;
}

.slide-fade-enter, .slide-fade-leave-to {
  transform: translateX(-10px);
  opacity: 0;
}

@media (max-width: 768px) {
  .file-manager {
    left: 5%;
    max-width: 80%;
    padding: 15px;
  }

  h2 {
    font-size: 1.5rem;
  }

  .file-link li {
    font-size: 0.9rem;
  }
}
</style>
