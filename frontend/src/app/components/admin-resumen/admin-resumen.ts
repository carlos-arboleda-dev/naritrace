import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { PanelApiService, EventoAuditoria } from '../../services/panel-api';
import { SesionService } from '../../services/sesion';
import { IconComponent } from '../icon/icon';

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

export function fechaCorta(iso: string): string {
  const d = new Date(iso);
  const dos = (n: number) => String(n).padStart(2, '0');
  return `${dos(d.getDate())} ${MESES[d.getMonth()]} · ${dos(d.getHours())}:${dos(d.getMinutes())}`;
}

@Component({
  selector: 'app-admin-resumen',
  standalone: true,
  imports: [RouterLink, IconComponent],
  templateUrl: './admin-resumen.html',
  styleUrl: './admin-resumen.css'
})
export class AdminResumenComponent implements OnInit {
  private api = inject(PanelApiService);
  sesion = inject(SesionService);

  d = signal<any | null>(null);
  error = signal('');
  verificando = signal(false);

  // filtros
  desde = signal('');
  hasta = signal('');
  departamento = signal('Nariño');
  municipio = signal('');
  municipios = signal<string[]>([]);

  // tabla de auditoría del resumen
  eventos = signal<EventoAuditoria[]>([]);
  totalEventos = signal(0);
  acciones = signal<string[]>([]);
  buscar = signal('');
  accion = signal('');
  resultado = signal('');
  private temporizador: ReturnType<typeof setTimeout> | undefined;

  fechaCorta = fechaCorta;
  num = (n: number) => (n ?? 0).toLocaleString('es-CO');

  saludoActualizado = computed(() => {
    const iso = this.d()?.actualizado;
    return iso ? fechaCorta(iso).replace(' · ', ', ') : '';
  });
  barrasMunicipio = computed(() => {
    const lista: { municipio: string; total: number }[] = this.d()?.lotes_por_municipio ?? [];
    const max = Math.max(...lista.map(x => x.total), 1);
    return lista.map(x => ({ ...x, ancho: (x.total / max) * 100 }));
  });
  barrasMes = computed(() => {
    const serie: { mes: string; total: number }[] = this.d()?.nuevos_lotes_mensual ?? [];
    const max = Math.max(...serie.map(s => s.total), 1);
    return serie.map((s, i) => ({ ...s, alto: Math.max((s.total / max) * 100, s.total ? 6 : 3), ultima: i === serie.length - 1 }));
  });
  mixMax = computed(() => Math.max(...(this.d()?.mix_productos ?? []).map((m: any) => m.total), 1));
  textoSolicitudes = computed(() => {
    const porRol: any[] = this.d()?.solicitudes_por_rol ?? [];
    return porRol.map(r => `${r.total} ${r.rol_display.toLowerCase()}${r.total === 1 ? '' : 'es'}`).join(' · ');
  });

  ngOnInit() {
    this.cargar();
    this.cargarEventos();
    this.api.adminMunicipios().subscribe({ next: m => this.municipios.set(m.map(x => x.municipio).sort()), error: () => {} });
  }

  cargar() {
    this.api.adminResumen({ desde: this.desde(), hasta: this.hasta(), departamento: this.departamento(), municipio: this.municipio() })
      .subscribe({
        next: r => {
          this.d.set(r); this.error.set('');
          if (!this.desde()) { this.desde.set(r.periodo.desde); this.hasta.set(r.periodo.hasta); }
        },
        error: () => this.error.set('No pudimos cargar el resumen regional.')
      });
  }

  cambiarFiltro(campo: 'desde' | 'hasta' | 'departamento' | 'municipio', valor: string) {
    this[campo].set(valor);
    this.cargar();
  }

  // ---- auditoría
  cargarEventos() {
    this.api.adminAuditoria({ page_size: 8, buscar: this.buscar(), accion: this.accion(), resultado: this.resultado() }).subscribe({
      next: r => { this.eventos.set(r.results); this.totalEventos.set(r.count); this.acciones.set(r.acciones); },
      error: () => {}
    });
  }
  alBuscar(v: string) {
    this.buscar.set(v);
    clearTimeout(this.temporizador);
    this.temporizador = setTimeout(() => this.cargarEventos(), 300);
  }
  filtrarEvento(campo: 'accion' | 'resultado', v: string) { this[campo].set(v); this.cargarEventos(); }

  // ---- integridad
  verificar() {
    this.verificando.set(true);
    this.api.adminVerificarCadena().subscribe({
      next: r => {
        const actual = this.d();
        if (actual) this.d.set({ ...actual, integridad: { ...actual.integridad, valida: r.valida, error: r.error, bloques: r.bloques, ultimo_hash: r.ultimo_hash } });
        this.verificando.set(false);
        this.cargarEventos();
      },
      error: () => { this.error.set('No pudimos verificar la cadena.'); this.verificando.set(false); }
    });
  }

  // ---- exportaciones (CSV)
  private descargar(nombre: string, filas: (string | number)[][]) {
    const csv = filas.map(f => f.map(c => `"${String(c ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a');
    a.href = url; a.download = nombre; a.click();
    URL.revokeObjectURL(url);
  }
  exportar() {
    const d = this.d(); if (!d) return;
    this.descargar('resumen-regional.csv', [
      ['Indicador', 'Valor'],
      ['Periodo', `${d.periodo.desde} a ${d.periodo.hasta}`],
      ['Productores activos', d.productores_activos], ['Lotes publicados', d.lotes_publicados],
      ['Eventos registrados', d.eventos_registrados], ['Solicitudes pendientes', d.solicitudes_pendientes],
      ['Consultas QR (30 días)', d.consultas_30d], ['Fincas con coordenadas (%)', d.eudr.pct_coordenadas],
      ['Fincas con polígono (%)', d.eudr.pct_poligono], ['Cadena íntegra', d.integridad.valida === null ? 'sin verificar' : d.integridad.valida ? 'sí' : 'NO'],
      [], ['Municipio', 'Lotes publicados'], ...d.lotes_por_municipio.map((m: any) => [m.municipio, m.total]),
      [], ['Mes', 'Nuevos lotes'], ...d.nuevos_lotes_mensual.map((m: any) => [m.mes, m.total]),
      [], ['Municipio', 'Productores'], ...d.productores_por_municipio.map((m: any) => [m.municipio, m.total]),
    ]);
  }
  descargarLogs() {
    this.api.adminAuditoria({ page_size: 500 }).subscribe(r => this.descargar('auditoria.csv', [
      ['Fecha', 'Usuario', 'Acción', 'Recurso', 'Detalle', 'Resultado'],
      ...r.results.map((e: EventoAuditoria) => [e.fecha, e.usuario, e.accion, e.recurso, e.detalle, e.resultado])]));
  }
}
