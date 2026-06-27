export interface Card {
  uid: string
  id: string
  merged_from: string[]
  images: string[]
  image_count: number
  title: string
  name_zh: string
  name_en: string
  dynasty: string
  material: string
  museum_id: string
  desc: string
  caption: string
  notes: string
  ex: string
  section: string
  type: 'artifact' | 'mixed' | 'label_only' | 'principle' | 'wall'
  status: 'complete' | 'pending_label' | 'partial'
  marker: string
  video: boolean
  highlight: boolean
  num: number
}

export interface Wall {
  ex: string
  section: string
  text: string
  img: string
  num: number
}

export interface Exhibition {
  key: string
  title: string
  short: string
  count: number
}

export interface Payload {
  schema_version: number
  generated: string
  meta: { total_cards: number; video_cards: number; exhibitions: number }
  exhibitions: Exhibition[]
  cards: Card[]
  walls: Wall[]
  ex_order: string[]
}
