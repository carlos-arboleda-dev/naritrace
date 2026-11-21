import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { PanelApiService } from '../../services/panel-api';
import { SesionService } from '../../services/sesion';
import { IconComponent } from '../icon/icon';
import { fechaCorta } from '../admin-resumen/admin-resumen';

type Accion = 'recibir' | 'despachar' | 'entregar';

const TEXTO_ACCION: Record<Accion, { titulo: string; boton: string; pide: string }> = {
  recibir: { titulo: 'Recibir lote', boton: 'Confirmar recepción', pide: '' },
  despachar: { titulo: 'Despachar lote', boton: 'Confirmar despacho', pide: 'Destino del despacho' },
  entregar: { titulo: 'Entregar al cliente', boton: 'Confirmar entrega', pide: 'Cliente o punto de entrega' },
};

@Component({
  selector: 'app-distribuidor-resumen',
  standalone: true,
  imports: [RouterLink, IconComponent],
  templateUrl: './distribuidor-resumen.html',
  styleUrl: './distribuidor-resumen.css'
})
export class DistribuidorResumenComponent implements OnInit {
  private api = inject(PanelApiService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  sesion = inject(SesionService);

  d = signal<any | null>(null);
  error = signal('');

  // panel de operación
  codigo = signal('');
  lote = signal<any | null>(null);
  buscando = signal(false);
  errorBusqueda = signal('');
  accion = signal<Accion | null>(null);
  destino = signal('');
  descripcion = signal('');
  tipoEnvio = signal('transporte');
  enviando = signal(false);
  exito = signal('');

  textos = TEXTO_ACCION;
  texto(a: string) { return TEXTO_ACCION[a as Accion]; }
  fechaCorta = fechaCorta;

  saludo = computed(() => {
    const h = new Date().getHours();
    const m = h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches';
    const n = this.sesion.usuario()?.first_name;
    return n ? `${m}, ${n}` : m;
  });
  semanas = computed(() => {
    const v: number[] = this.d()?.movimientos_semanales ?? [];
    const max = Math.max(...v, 1);
    const nombres = ['Hace 5 sem', 'Hace 4', 'Hace 3', 'Hace 2', 'Pasada', 'Esta'];
    return v.map((n, i) => ({ n, etiqueta: nombres[i], alto: Math.max((n / max) * 100, n ? 6 : 3), ultima: i === v.length - 1 }));
  });

  ngOnInit() {
    this.cargar();
    const c = this.route.snapshot.queryParamMap.get('codigo');
    if (c) { this.codigo.set(c); this.buscar(); }
  }

  cargar() {
    this.api.distResumen().subscribe({ next: r => this.d.set(r), error: () => this.error.set('No pudimos cargar tu panel de operaciones.') });
  }

  /** Acepta un código o un enlace completo copiado del QR. */
  private extraerCodigo(texto: string): string {
    const m = texto.toUpperCase().match(/NT-\d{6}-\d{3}/);
    return (m ? m[0] : texto.trim().toUpperCase());
  }

  buscar(codigo?: string, conservarExito = false) {
    const c = this.extraerCodigo(codigo ?? this.codigo());
    if (!c) return;
    this.codigo.set(c);
    this.buscando.set(true); this.errorBusqueda.set(''); this.accion.set(null);
    if (!conservarExito) this.exito.set('');
    this.api.buscarLote(c).subscribe({
      next: l => { this.lote.set(l); this.buscando.set(false); },
      error: e => { this.lote.set(null); this.buscando.set(false); this.errorBusqueda.set(e?.error?.error ?? 'No pudimos buscar el lote.'); }
    });
  }

  limpiar() { this.lote.set(null); this.codigo.set(''); this.accion.set(null); this.exito.set(''); this.errorBusqueda.set(''); }

  elegir(a: Accion) {
    this.accion.set(a); this.destino.set(''); this.descripcion.set(''); this.errorBusqueda.set('');
  }

  confirmar() {
    const a = this.accion(); const l = this.lote();
    if (!a || !l) return;
    if (a !== 'recibir' && !this.destino().trim()) { this.errorBusqueda.set(`Indica: ${TEXTO_ACCION[a].pide.toLowerCase()}.`); return; }
    this.enviando.set(true); this.errorBusqueda.set('');
    this.api.operar({ codigo: l.codigo, accion: a, destino: this.destino(), descripcion: this.descripcion(), tipo_envio: this.tipoEnvio() }).subscribe({
      next: r => {
        this.enviando.set(false); this.accion.set(null); this.exito.set(r.mensaje);
        this.cargar();
        this.buscar(l.codigo, true);     // refresca ficha y línea de tiempo
        setTimeout(() => this.exito.set(''), 6000);
      },
      error: e => { this.enviando.set(false); this.errorBusqueda.set(e?.error?.error ?? 'No se pudo registrar la operación.'); }
    });
  }

  verPublica(codigo: string) { window.open(`/trazabilidad/${codigo}`, '_blank'); }
  verMas(vista: string) { this.router.navigate(['/dashboard/inventario'], { queryParams: { vista } }); }
  etiquetaEstado(e: string) { return e === 'publicado' ? 'En custodia' : e === 'en_transito' ? 'En tránsito' : e === 'entregado' ? 'Entregado' : e; }
}
