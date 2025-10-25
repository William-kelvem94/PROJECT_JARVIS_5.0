import { useEffect } from 'react'

interface ToastProps {
  message: string
  type?: 'success' | 'error' | 'info'
}

export const Toaster = () => {
  return <div id="toast-container" className="fixed top-4 right-4 z-50 space-y-2" />
}

export const toast = ({ message, type = 'info' }: ToastProps) => {
  const container = document.getElementById('toast-container')
  if (!container) return

  const toastEl = document.createElement('div')
  toastEl.className = `
    card p-4 min-w-[300px] animate-in slide-in-from-right
    ${type === 'success' ? 'border-green-500' : ''}
    ${type === 'error' ? 'border-red-500' : ''}
    ${type === 'info' ? 'border-blue-500' : ''}
  `

  toastEl.innerHTML = `
    <div class="flex items-center gap-3">
      <div class="flex-1 text-sm">${message}</div>
      <button class="text-gray-400 hover:text-white">×</button>
    </div>
  `

  const closeBtn = toastEl.querySelector('button')
  closeBtn?.addEventListener('click', () => {
    toastEl.classList.add('animate-out', 'fade-out')
    setTimeout(() => toastEl.remove(), 300)
  })

  container.appendChild(toastEl)

  setTimeout(() => {
    toastEl.classList.add('animate-out', 'fade-out')
    setTimeout(() => toastEl.remove(), 300)
  }, 5000)
}

