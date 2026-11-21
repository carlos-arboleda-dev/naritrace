import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { PanelApiService } from '../../services/panel-api';
import { IconComponent } from '../icon/icon';
import { fechaCorta } from '../admin-resumen/admin-resumen';

type Vista = 'productores' | 'lotes' | 'municipios' | 'auditoria' | 'solicitudes';

const TITULOS: Record<Vista, { t: string; s: string }> = {
  productores: { t: 'Productores', s: 'Quién produce, dónde y cuánto ha publicado. Verifica a los productores confiables.' },
  lotes: { t: 'Lotes publicados', s: 'Todos los lotes sellados en el registro encadenado. Comprueba su integridad en un clic.' },
  municipios: { t: 'Municipios', s: 'Cobertura territorial: productores, fincas, lotes y geolocalización por municipio.' },
  auditoria: { t: 'Auditoría', s: 'Historial de solo lectura: quién hizo qué y cuándo.' },
  solicitudes: { t: 'Solicitudes de rol', s: 'Aprueba o rechaza quién entra a la cadena como productor, distribuidor, acopiador o transportador.' },
};

/** Una sola pantalla para las 5 secciones de listado del administrador (se elige por la ruta). */
@Component({
  selector: 'app-admin-seccion',
  standalone: true,
  imports: [IconComponent],
  templateUrl: './admin-seccion.html',
  styleUrl: './admin-seccion.css'
})
export class AdminSeccionComponent implements OnInit {
  private api = inject(PanelApiService);
  vista = inject(ActivatedRoute).snapshot.data['vista'] as Vista;
  titulo = TITULOS[this.vista];

  filas = signal<any[]>([]);
  cargando = signal(true);
  error = signal('');
  mensaje = signal('');
  buscar = signal('');
  filtro = signal('');            // estado / resultado / acción, según la vista
  filtroAccion = signal('');
  acciones = signal<string[]>([]);
  pagina = signal(1);
  total = signal(0);
  verificaciones = signal<Record<number, { valida: boolean; texto: string }>>({});
  ocupado = signal<number | null>(null);
  private temporizador: ReturnType<typeof setTimeout> | undefined;

  fechaCorta = fechaCorta;
  porPagina = 15;
  totalPaginas = computed(() => Math.max(Math.ceil(this.total() / this.porPagina), 1));

  ngOnInit() { this.cargar(); }

  cargar() {
    this.cargando.set(true); this.error.set('');
    const fallo = () => { this.error.set('No pudimos cargar la información.'); this.cargando.set(false); };
    const listo = (f: any[]) => { this.filas.set(f); this.cargando.set(false); };
    const b = this.buscar();
    switch (this.vista) {
      case 'productores': this.api.adminProductores(b).subscribe({ next: listo, error: fallo }); break;
      case 'lotes': this.api.adminLotes({ buscar: b, estado: this.filtro() }).subscribe({ next: listo, error: fallo }); break;
      case 'municipios': this.api.adminMunicipios().subscribe({ next: listo, error: fallo }); break;
      case 'solicitudes': this.api.adminSolicitudes(this.filtro() || 'pendiente').subscribe({ next: listo, error: fallo }); break;
      case 'auditoria':
        this.api.adminAuditoria({ page: this.pagina(), page_size: this.porPagina, buscar: b, accion: this.filtroAccion(), resultado: this.filtro() })
          .subscribe({ next: r => { this.total.set(r.count); this.acciones.set(r.acciones); listo(r.results); }, error: fallo });
        break;
    }
  }

  alBuscar(v: string) {
    this.buscar.set(v);
    clearTimeout(this.temporizador);
    this.temporizador = setTimeout(() => { this.pagina.set(1); this.cargar(); }, 300);
  }
  alFiltrar(v: string) { this.filtro.set(v); this.pagina.set(1); this.cargar(); }
  alFiltrarAccion(v: string) { this.filtroAccion.set(v); this.pagina.set(1); this.cargar(); }
  irA(n: number) { if (n >= 1 && n <= this.totalPaginas()) { this.pagina.set(n); this.cargar(); } }

  // ---- acciones
  alternarVerificado(p: any) {
    this.ocupado.set(p.id);
    this.api.adminVerificarProductor(p.id).subscribe({
      next: r => { p.verificado = r.verificado; this.filas.set([...this.filas()]); this.ocupado.set(null); },
      error: () => { this.error.set('No se pudo cambiar la verificación.'); this.ocupado.set(null); }
    });
  }

  verificarLote(l: any) {
    this.ocupado.set(l.id);
    this.api.adminVerificarLote(l.id).subscribe({
      next: r => {
        this.verificaciones.update(v => ({ ...v, [l.id]: { valida: r.valida, texto: r.valida ? `Íntegro · ${r.bloques} bloques` : (r.error ?? 'Alterado') } }));
        this.ocupado.set(null);
      },
      error: () => { this.error.set('No se pudo verificar el lote.'); this.ocupado.set(null); }
    });
  }

  resolver(s: any, decision: 'aprobar' | 'rechazar') {
    const nota = decision === 'rechazar' ? (window.prompt('Motivo (opcional) para el solicitante:') ?? '') : '';
    this.ocupado.set(s.id);
    this.api.adminResolver(s.id, decision, nota).subscribe({
      next: () => {
        this.mensaje.set(`${s.nombre}: solicitud ${decision === 'aprobar' ? 'aprobada' : 'rechazada'}.`);
        this.ocupado.set(null);
        this.cargar();
      },
      error: e => { this.error.set(e?.error?.error ?? 'No se pudo resolver la solicitud.'); this.ocupado.set(null); }
    });
  }

  exportar() {
    const f = this.filas();
    if (!f.length) return;
    const cols = Object.keys(f[0]).filter(k => typeof f[0][k] !== 'object' || f[0][k] === null);
    const csv = [cols, ...f.map(r => cols.map(c => r[c]))].map(fila => fila.map(c => `"${String(c ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = `${this.vista}.csv`; a.click(); URL.revokeObjectURL(url);
  }
}
