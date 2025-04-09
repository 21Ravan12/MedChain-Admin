<template>
    <div class="dropdown" v-click-outside="close">
      <div @click="toggle">
        <slot name="trigger"></slot>
      </div>
      
      <transition name="dropdown">
        <div 
          v-show="isOpen"
          class="dropdown-menu"
          :style="menuStyle"
          :class="[placement, { 'dropdown-menu-up': up }]"
        >
          <slot></slot>
        </div>
      </transition>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DropdownMenu',
    props: {
      placement: {
        type: String,
        default: 'left',
        validator: value => ['left', 'right'].includes(value)
      },
      up: Boolean
    },
    data() {
      return {
        isOpen: false
      }
    },
    computed: {
      menuStyle() {
        return this.up ? { bottom: '100%', top: 'auto' } : {};
      }
    },
    methods: {
      toggle() {
        this.isOpen = !this.isOpen;
      },
      close() {
        this.isOpen = false;
      }
    },
    directives: {
      'click-outside': {
        bind(el, binding, vnode) {
          el.clickOutsideEvent = function(event) {
            if (!(el === event.target || el.contains(event.target))) {
              vnode.context[binding.expression](event);
            }
          };
          document.body.addEventListener('click', el.clickOutsideEvent);
        },
        unbind(el) {
          document.body.removeEventListener('click', el.clickOutsideEvent);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .dropdown {
    position: relative;
    display: inline-block;
  }
  
  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 1000;
    min-width: 180px;
    padding: 0.5rem 0;
    margin: 0.125rem 0 0;
    font-size: 0.875rem;
    color: #212529;
    text-align: left;
    background-color: #fff;
    background-clip: padding-box;
    border: 1px solid rgba(0, 0, 0, 0.15);
    border-radius: 0.25rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.175);
    
    &.right {
      left: auto;
      right: 0;
    }
    
    &.dropdown-menu-up {
      bottom: 100%;
      top: auto;
    }
  }
  
  .dropdown-enter-active,
  .dropdown-leave-active {
    transition: all 0.2s ease;
  }
  
  .dropdown-enter,
  .dropdown-leave-to {
    opacity: 0;
    transform: translateY(-10px);
  }
  </style>