<template>
  <NavBar />
  <router-view />
</template>

<script>
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: {
    NavBar
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #1a1a1a;
  color: #ffffff;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

* {
  box-sizing: border-box;
}
</style>