import React, { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { InformationCircleIcon } from '@heroicons/react/24/outline'

const SmartTooltip = ({ 
  children, 
  content, 
  placement = 'top', 
  delay = 500,
  interactive = false,
  showArrow = true,
  className = '',
  ...props 
}) => {
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const triggerRef = useRef(null)
  const tooltipRef = useRef(null)
  const timeoutRef = useRef(null)

  const showTooltip = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => {
      calculatePosition()
      setIsVisible(true)
    }, delay)
  }

  const hideTooltip = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    if (!interactive) {
      setIsVisible(false)
    }
  }

  const calculatePosition = () => {
    if (!triggerRef.current) return

    const triggerRect = triggerRef.current.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    
    let x, y

    switch (placement) {
      case 'top':
        x = triggerRect.left + triggerRect.width / 2
        y = triggerRect.top - 8
        break
      case 'bottom':
        x = triggerRect.left + triggerRect.width / 2
        y = triggerRect.bottom + 8
        break
      case 'left':
        x = triggerRect.left - 8
        y = triggerRect.top + triggerRect.height / 2
        break
      case 'right':
        x = triggerRect.right + 8
        y = triggerRect.top + triggerRect.height / 2
        break
      default:
        x = triggerRect.left + triggerRect.width / 2
        y = triggerRect.top - 8
    }

    // Viewport boundary adjustments
    if (x < 8) x = 8
    if (x > viewportWidth - 200) x = viewportWidth - 200
    if (y < 8) y = 8
    if (y > viewportHeight - 100) y = viewportHeight - 100

    setPosition({ x, y })
  }

  useEffect(() => {
    const handleScroll = () => {
      if (isVisible) {
        calculatePosition()
      }
    }

    const handleResize = () => {
      if (isVisible) {
        calculatePosition()
      }
    }

    window.addEventListener('scroll', handleScroll, true)
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('scroll', handleScroll, true)
      window.removeEventListener('resize', handleResize)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [isVisible])

  const tooltip = isVisible && (
    <div
      ref={tooltipRef}
      className={`fixed z-50 px-3 py-2 text-sm bg-gray-900 text-white rounded-lg shadow-lg max-w-xs transition-opacity duration-200 ${className}`}
      style={{
        left: placement === 'left' ? position.x - 200 : placement === 'right' ? position.x : position.x - 100,
        top: placement === 'top' ? position.y - 40 : placement === 'bottom' ? position.y : position.y - 20,
        transform: placement === 'left' || placement === 'right' ? 'translateY(-50%)' : 'translateX(50%)'
      }}
      onMouseEnter={() => interactive && setIsVisible(true)}
      onMouseLeave={() => interactive && setIsVisible(false)}
      role="tooltip"
      aria-hidden={!isVisible}
    >
      {content}
      {showArrow && (
        <div
          className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
            placement === 'top' ? 'bottom-0 left-1/2 translate-x-[-50%] translate-y-1/2' :
            placement === 'bottom' ? 'top-0 left-1/2 translate-x-[-50%] translate-y-[-50%]' :
            placement === 'left' ? 'right-0 top-1/2 translate-x-1/2 translate-y-[-50%]' :
            'left-0 top-1/2 translate-x-[-50%] translate-y-[-50%]'
          }`}
        />
      )}
    </div>
  )

  return (
    <>
      <span
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        className="inline-block"
        {...props}
      >
        {children}
      </span>
      {typeof document !== 'undefined' && createPortal(tooltip, document.body)}
    </>
  )
}

// Helper component for info icons with tooltips
export const InfoTooltip = ({ content, className = '' }) => (
  <SmartTooltip content={content} placement="top">
    <InformationCircleIcon className={`w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help ${className}`} />
  </SmartTooltip>
)

export default SmartTooltip