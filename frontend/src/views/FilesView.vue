<template>
    <div class="file-manager">
      <h2>Uploaded Files</h2>
      <ul v-if="files.length">
        <li v-for="file in files" :key="file.name">
          <!-- Update the link to point to the /files path -->
          <router-link :to="`/files/${encodeURIComponent(file.name)}`" target="_blank">
            {{ file.name }}
          </router-link>
          
        </li>
      </ul>
      <p v-else>No files uploaded yet.</p>
      <p v-if="error" class="error">{{ error }}</p>
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
    max-width: 700px;
    margin: 40px auto;
    padding: 20px;
    background-color: #f9f9f9;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    text-align: center;
    font-family: 'Arial', sans-serif;
  }
  
  h2 {
    color: #333;
    font-size: 1.8rem;
    margin-bottom: 20px;
  }
  
  ul {
    list-style: none;
    padding: 0;
  }
  
  li {
    margin: 10px 0;
  }
  
  a {
    color: #007bff;
    font-size: 1.2rem;
    font-weight: 500;
    text-decoration: none;
    transition: color 0.3s ease;
  }
  
  a:hover {
    color: #0056b3;
  }
  
  .error {
    color: red;
    font-size: 1.1rem;
    margin-top: 20px;
  }
  
  p {
    font-size: 1.1rem;
    color: #666;
  }
  
  @media (max-width: 768px) {
    .file-manager {
      padding: 15px;
      font-size: 0.9rem;
    }
  
    h2 {
      font-size: 1.5rem;
    }
  
    a {
      font-size: 1rem;
    }
  }
  </style>
  