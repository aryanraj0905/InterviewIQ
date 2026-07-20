import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface HealthResponse {
  status: string
  service: string
  version: string
  environment: string
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/v1/health')
      .then((res) => {
        if (!res.ok) throw new Error(`Request failed: ${res.status}`)
        return res.json() as Promise<HealthResponse>
      })
      .then(setHealth)
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <main className="flex min-h-svh items-center justify-center bg-background p-6">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="w-[380px]">
          <CardHeader>
            <CardTitle>AI Interview Intelligence Platform</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {error && (
              <p className="text-sm text-destructive">
                Backend unreachable: {error}
              </p>
            )}
            {!error && !health && (
              <p className="text-sm text-muted-foreground">
                Checking backend connection…
              </p>
            )}
            {health && (
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Status</span>
                  <Badge variant={health.status === 'ok' ? 'default' : 'destructive'}>
                    {health.status}
                  </Badge>
                </div>
                <p>
                  <span className="text-muted-foreground">Service:</span>{' '}
                  {health.service}
                </p>
                <p>
                  <span className="text-muted-foreground">Version:</span>{' '}
                  {health.version}
                </p>
                <p>
                  <span className="text-muted-foreground">Environment:</span>{' '}
                  {health.environment}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </main>
  )
}

export default App
