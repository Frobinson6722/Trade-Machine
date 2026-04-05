import { useEffect, useRef, useCallback, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import type { WSMessage } from '../lib/types'

const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const queryClient = useQueryClient()
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout>>()

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data)
        setLastMessage(msg)

        // Invalidate relevant queries based on message type
        switch (msg.type) {
          case 'trade_update':
            queryClient.invalidateQueries({ queryKey: ['trades'] })
            queryClient.invalidateQueries({ queryKey: ['portfolio'] })
            break
          case 'agent_activity':
            queryClient.invalidateQueries({ queryKey: ['agent-logs'] })
            break
          case 'pnl_tick':
            queryClient.invalidateQueries({ queryKey: ['portfolio'] })
            queryClient.invalidateQueries({ queryKey: ['equity-curve'] })
            break
          case 'status_change':
            queryClient.invalidateQueries({ queryKey: ['session-status'] })
            break
        }
      } catch {
        // Ignore unparseable messages
      }
    }

    ws.onclose = () => {
      setConnected(false)
      // Auto-reconnect after 3 seconds
      reconnectTimeout.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [queryClient])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimeout.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { connected, lastMessage }
}
