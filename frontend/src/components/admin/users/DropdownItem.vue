<template>
  <button
    class="dropdown-item"
    :class="{ 'danger': danger }"
    @click="$emit('click')"
  >
    <i v-if="icon" :class="icon"></i>
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'DropdownItem',
  props: {
    icon: String,
    danger: Boolean
  }
}
</script>

<style scoped>
.dropdown-item {
  display: block;
  width: 100%;
  padding: 0.5rem 1.5rem;
  clear: both;
  font-weight: 400;
  color: #212529;
  text-align: inherit;
  white-space: nowrap;
  background-color: transparent;
  border: 0;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    color: #16181b;
    text-decoration: none;
    background-color: #f8f9fa;
  }
  
  &:focus {
    outline: 0;
    color: #16181b;
    background-color: #f8f9fa;
  }
  
  &.danger {
    color: #dc3545;
    
    &:hover, &:focus {
      color: #fff;
      background-color: #dc3545;
    }
  }
  
  i {
    margin-right: 0.5rem;
    width: 1em;
    text-align: center;
  }
}
</style>