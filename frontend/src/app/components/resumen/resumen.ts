import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService, Lote, Pagina, Producto, Usuario } from '../../services/api';
import { IconComponent } from '../icon/icon';

type LoteFila = Lote & { total_movimientos: number };

interface Estadisticas {
  lotes_registrados: number;
  lotes_disponibles: number;
  lotes_borrador: number;
  lotes_en_transito: number;
  nuevos_este_mes: number;
  movimientos_registrados: number;
  movimientos_lote_destacado: number;
  consultas_30d: number;
  consultas_semana: number;
  consultas_mensuales: { mes: string; total: number }[];
  consultas_rango: string;
  borrador_pendiente: { id: number; codigo: string; producto: string; mes_cosecha: string } | null;
  actualizado: string;
}

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
const POR_PAGINA = 6;

/** Etiquetas visibles del estado ("publicado" se muestra como "Disponible"). */
const ETIQUETA_ESTADO: Record<string, string> = {
  publicado: 'Disponible', en_transito: 'En tránsito', borrador: 'Borrador',
  entregado: 'Entregado', archivado: 'Archivado',
};

@Component({
  selector: 'app-resumen',
  standalone: true,
  imports: [RouterLink, IconComponent],
  templateUrl: './resumen.html',
  styleUrl: './resumen.css'
})
export class ResumenComponent implements OnInit {
  private api = inject(ApiService);

  usuario = signal<Usuario | null>(null);
  stats = signal<Estadisticas | null>(null);
  pagina = signal<Pagina<LoteFila> | null>(null);
  productos = signal<Producto[]>([]);
  cargando = signal(true);
  error = signal('');

  // Filtros de la tabla
  busqueda = signal('');
  estado = signal('');
  producto = signal('');
  numeroPagina = signal(1);
  private temporizador: ReturnType<typeof setTimeout> | undefined;

  saludo = computed(() => {
    const h = new Date().getHours();
    const momento = h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches';
    const nombre = this.usuario()?.first_name || this.usuario()?.username || '';
    return nombre ? `${momento}, ${nombre}` : momento;
  });

  actualizado = computed(() => {
    const iso = this.stats()?.actualizado;
    if (!iso) return '';
    const d = new Date(iso);
    const dos = (n: number) => String(n).padStart(2, '0');
    return `${dos(d.getDate())} ${MESES[d.getMonth()]} ${d.getFullYear()}, ${dos(d.getHours())}:${dos(d.getMinutes())}`;
  });

  /** Altura de cada barra (0–100) relativa al mes con más consultas. */
  barras = computed(() => {
    const serie = this.stats()?.consultas_mensuales ?? [];
    const max = Math.max(...serie.map(s => s.total), 1);
    return serie.map((s, i) => ({
      ...s, alto: Math.max((s.total / max) * 100, s.total > 0 ? 6 : 3), ultima: i === serie.length - 1
    }));
  });

  totalPaginas = computed(() => Math.max(Math.ceil((this.pagina()?.count ?? 0) / POR_PAGINA), 1));
  paginas = computed(() => Array.from({ length: this.totalPaginas() }, (_, i) => i + 1));

  ngOnInit() {
    this.api.getMe().subscribe({ next: u => this.usuario.set(u), error: () => {} });
    this.api.getEstadisticas().subscribe({
      next: e => this.stats.set(e),
      error: () => this.error.set('No pudimos cargar tus estadísticas.')
    });
    this.api.getProductosLista().subscribe({ next: r => this.productos.set(r.results), error: () => {} });
    this.cargarLotes();
  }

  cargarLotes() {
    this.cargando.set(true);
    this.api.getLotesPagina({
      page: this.numeroPagina(), page_size: POR_PAGINA,
      search: this.busqueda(), estado: this.estado(), producto: this.producto()
    }).subscribe({
      next: p => { this.pagina.set(p); this.cargando.set(false); },
      error: () => { this.error.set('No pudimos cargar tus lotes.'); this.cargando.set(false); }
    });
  }

  // ---- eventos de filtros
  alBuscar(valor: string) {
    this.busqueda.set(valor);
    clearTimeout(this.temporizador);
    this.temporizador = setTimeout(() => { this.numeroPagina.set(1); this.cargarLotes(); }, 300);
  }
  alFiltrar(campo: 'estado' | 'producto', valor: string) {
    this[campo].set(valor);
    this.numeroPagina.set(1);
    this.cargarLotes();
  }
  irAPagina(n: number) {
    if (n < 1 || n > this.totalPaginas() || n === this.numeroPagina()) return;
    this.numeroPagina.set(n);
    this.cargarLotes();
  }

  // ---- presentación
  etiquetaEstado(e: string) { return ETIQUETA_ESTADO[e] ?? e; }

  codigo(l: LoteFila) { return l.codigo && l.estado !== 'borrador' ? l.codigo : 'Borrador sin código'; }

  cantidad(l: LoteFila) {
    const n = Number(l.cantidad);
    if (l.estado === 'borrador' && !n) return 'Por definir';
    return `${n.toLocaleString('es-CO', { maximumFractionDigits: 2 })} ${l.unidad}`;
  }

  fecha(iso: string) {
    const [a, m, d] = iso.split('-').map(Number);   // sin pasar por Date: evita desfase de zona horaria
    return `${String(d).padStart(2, '0')} ${MESES[m - 1]} ${a}`;
  }

  eventos(l: LoteFila) {
    const n = l.total_movimientos;
    return n ? `${n} ${n === 1 ? 'evento' : 'eventos'}` : '— eventos';
  }

  plural(n: number, uno: string, varios: string) { return `${n} ${n === 1 ? uno : varios}`; }

  // ---- exportar CSV (respeta los filtros activos)
  exportar() {
    this.api.getLotesPagina({
      page_size: 500, search: this.busqueda(), estado: this.estado(), producto: this.producto()
    }).subscribe(p => {
      const filas = [['Código', 'Producto', 'Finca', 'Cantidad', 'Unidad', 'Cosecha', 'Estado', 'Eventos'],
        ...p.results.map(l => [l.codigo ?? '', l.producto_nombre, l.finca_nombre, l.cantidad, l.unidad,
          l.fecha_cosecha, this.etiquetaEstado(l.estado), String(l.total_movimientos)])];
      const csv = filas.map(f => f.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
      const url = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
      const a = document.createElement('a');
      a.href = url; a.download = 'mis-lotes.csv'; a.click();
      URL.revokeObjectURL(url);
    });
  }
}
