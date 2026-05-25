<template>
  <div v-if="graph?.nodes?.length" class="handoff-graph">
    <svg :width="svgWidth" :height="svgHeight" :viewBox="`0 0 ${svgWidth} ${svgHeight}`">
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
        </marker>
      </defs>

      <g v-for="edge in graph.edges" :key="edge.handoff_id || `${edge.from}-${edge.to}`">
        <line
          :x1="getNodeCenter(edge.from).x"
          :y1="getNodeCenter(edge.from).y"
          :x2="getNodeCenter(edge.to).x"
          :y2="getNodeCenter(edge.to).y"
          stroke="#94a3b8"
          stroke-width="2"
          marker-end="url(#arrowhead)"
        />
        <text
          :x="(getNodeCenter(edge.from).x + getNodeCenter(edge.to).x) / 2"
          :y="(getNodeCenter(edge.from).y + getNodeCenter(edge.to).y) / 2 - 10"
          text-anchor="middle"
          font-size="12"
          fill="#64748b"
        >
          {{ edge.reason || 'handoff' }}
        </text>
      </g>

      <g v-for="node in graph.nodes" :key="node.id">
        <rect
          :x="getNodePosition(node.id).x"
          :y="getNodePosition(node.id).y"
          :width="NODE_WIDTH"
          :height="NODE_HEIGHT"
          :rx="12"
          :fill="getNodeColor(node.type)"
        />
        <text
          :x="getNodeCenter(node.id).x"
          :y="getNodeCenter(node.id).y + 5"
          text-anchor="middle"
          font-size="13"
          fill="#ffffff"
          font-weight="600"
        >
          {{ node.label }}
        </text>
      </g>
    </svg>
  </div>
  <a-empty v-else description="暂无 Handoff 流程图" />
</template>

<script setup lang="ts">
const NODE_WIDTH = 160
const NODE_HEIGHT = 44
const NODE_GAP = 56

interface GraphNode {
  id: string
  label: string
  type: string
}

interface GraphEdge {
  from: string
  to: string
  reason?: string
  handoff_id?: string
}

const props = defineProps<{
  graph?: {
    nodes: GraphNode[]
    edges: GraphEdge[]
  } | null
}>()

const svgWidth = 240 + Math.max(0, (props.graph?.nodes?.length || 1) - 1) * (NODE_WIDTH + NODE_GAP)
const svgHeight = 180

function getNodePosition(nodeId: string) {
  const index = props.graph?.nodes?.findIndex((node) => node.id === nodeId) ?? 0
  return {
    x: 40 + index * (NODE_WIDTH + NODE_GAP),
    y: 72,
  }
}

function getNodeCenter(nodeId: string) {
  const pos = getNodePosition(nodeId)
  return {
    x: pos.x + NODE_WIDTH / 2,
    y: pos.y + NODE_HEIGHT / 2,
  }
}

function getNodeColor(type: string) {
  if (type === 'supervisor') return '#2563eb'
  if (type === 'approval') return '#f97316'
  return '#16a34a'
}
</script>

<style scoped>
.handoff-graph {
  width: 100%;
  overflow-x: auto;
  padding: 12px 0;
}
</style>
