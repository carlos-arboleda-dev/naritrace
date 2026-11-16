import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { QRCodeComponent } from 'angularx-qrcode';
import { ApiService, Finca, Producto, Usuario } from '../../services/api';
import { IconComponent } from '../icon/icon';

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

const VARIEDADES: Record<string, string[]> = {
  cafe: ['Castillo', 'Caturra', 'Colombia', 'Típica', 'Borbón', 'Tabi', 'Geisha'],
  cacao: ['CCN-51', 'Criollo', 'Trinitario', 'Forastero'],
  frutas: ['Hass', 'Lulo de Castilla', 'Mora de Castilla', 'Granadilla'],
  acuicultura: ['Trucha arcoíris', 'Tilapia roja'],
  pancoger: ['Papa criolla', 'Maíz', 'Fríjol', 'Yuca'],
};
const OTRA = '__otra__';

export const PROCESOS = ['Lavado', 'Honey', 'Natural', 'Seco', 'Fermentado', 'Otro'];
export const UNIDADES = [
  { valor: 'kg', texto: 'Kilogramos (kg)' }, { valor: 'lb', texto: 'Libras (lb)' },
  { valor: 't', texto: 'Toneladas (t)' }, { valor: 'und', texto: 'Unidades (und)' },
];

interface Publicado { codigo: string; qr_codigo: string; lote: any; }

@Component({
  selector: 'app-crear-lote',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, QRCodeComponent, IconComponent],
  templateUrl: './crear-lote.html',
  styleUrl: './crear-lote.css'
})
export class CrearLoteComponent implements OnInit {
  private fb = inject(FormBuilder);
  private api = inject(ApiService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  readonly OTRA = OTRA;
  readonly procesos = PROCESOS;
  readonly unidades = UNIDADES;

  paso = signal<1 | 2 | 3 | 4>(1);
  productos = signal<Producto[]>([]);
  fincas = signal<Finca[]>([]);
  usuario = signal<Usuario | null>(null);
  loteId = signal<number | null>(null);
  publicado = signal<Publicado | null>(null);
  guardando = signal(false);
  intentado = signal(false);       // se activa al pulsar "continuar" con errores
  mensaje = signal('');            // confirmaciones ("Borrador guardado…")
  error = signal('');
  copiado = signal(false);

  form = this.fb.group({
    producto: ['', Validators.required],
    variedadSel: ['', Validators.required],
    variedadOtra: [''],
    cantidad: [null as number | null, [Validators.required, Validators.min(0.01)]],
    unidad: ['kg', Validators.required],
    fecha_cosecha: ['', Validators.required],
    proceso: [''],
    finca: ['', Validators.required],
    notas_produccion: [''],
    confirmo: [false],
  });
  v = toSignal(this.form.valueChanges, { initialValue: this.form.getRawValue() });

  // ---------- datos derivados
  productoSel = computed(() => this.productos().find(p => String(p.id) === String(this.v().producto)));
  opcionesVariedad = computed(() => VARIEDADES[this.productoSel()?.categoria ?? ''] ?? []);
  fincaSel = computed(() => this.fincas().find(f => String(f.id) === String(this.v().finca)));
  variedad = computed(() => this.v().variedadSel === OTRA ? (this.v().variedadOtra ?? '').trim() : (this.v().variedadSel ?? ''));
  nombreFinca = computed(() => (this.fincaSel()?.nombre ?? '').replace(/^Finca\s+/i, ''));
  ubicacion = computed(() => {
    const f = this.fincaSel();
    return f ? [f.municipio, f.departamento].filter(Boolean).join(', ') : '—';
  });
  responsable = computed(() => {
    const u = this.usuario();
    return u ? (`${u.first_name} ${u.last_name}`.trim() || u.username) : '—';
  });
  cantidadTexto = computed(() => {
    const n = Number(this.v().cantidad);
    return n > 0 ? `${n.toLocaleString('es-CO', { maximumFractionDigits: 2 })} ${this.v().unidad}` : 'Por definir';
  });
  productoTexto = computed(() => {
    const p = this.productoSel()?.nombre;
    if (!p) return '—';
    return this.variedad() ? `${p} · ${this.variedad()}` : p;
  });
  fechaTexto = computed(() => this.fecha(this.v().fecha_cosecha ?? ''));
  latitudTexto = computed(() => this.coord(this.fincaSel()?.latitud, 'N', 'S'));
  longitudTexto = computed(() => this.coord(this.fincaSel()?.longitud, 'E', 'O'));
  areaTexto = computed(() => {
    const a = this.fincaSel()?.area_hectareas;
    return a ? `${Number(a).toLocaleString('es-CO', { maximumFractionDigits: 2 })} ha` : 'No registrada';
  });
  hintCantidad = computed(() => this.productoSel()?.categoria === 'cafe' ? 'Peso de café pergamino seco.' : '');

  // ---------- ciclo de vida
  ngOnInit() {
    this.api.getMe().subscribe({ next: u => this.usuario.set(u), error: () => {} });
    this.api.getProductosLista().subscribe(r => this.productos.set(r.results));
    this.api.getFincas().subscribe((r: any) => {
      const lista: Finca[] = r.results ?? r;
      this.fincas.set(lista);
      if (lista.length === 1 && !this.form.value.finca) this.form.patchValue({ finca: String(lista[0].id) });
      this.cargarBorrador();
    });
    // Al cambiar de producto, la variedad anterior deja de aplicar
    this.form.controls.producto.valueChanges.subscribe(() =>
      this.form.patchValue({ variedadSel: '', variedadOtra: '' }, { emitEvent: true }));
  }

  /** Si se llega con ?borrador=ID se retoma ese lote. */
  private cargarBorrador() {
    const id = Number(this.route.snapshot.queryParamMap.get('borrador'));
    if (!id) return;
    this.api.getLote(id).subscribe({
      next: l => {
        if (l.estado !== 'borrador') { this.router.navigate(['/dashboard/lotes', id]); return; }
        this.loteId.set(id);
        const opciones = VARIEDADES[l.producto?.categoria] ?? [];
        const enLista = opciones.includes(l.variedad);
        this.form.patchValue({
          producto: String(l.producto.id), finca: String(l.finca.id),
          variedadSel: l.variedad ? (enLista ? l.variedad : OTRA) : '',
          variedadOtra: enLista ? '' : (l.variedad ?? ''),
          cantidad: Number(l.cantidad) || null, unidad: l.unidad, fecha_cosecha: l.fecha_cosecha,
          proceso: l.proceso ?? '', notas_produccion: l.notas_produccion ?? '',
        }, { emitEvent: false });
        // patchValue con emitEvent:false no actualiza v(); lo forzamos
        this.form.updateValueAndValidity({ emitEvent: true });
        this.form.patchValue({ variedadSel: l.variedad ? (enLista ? l.variedad : OTRA) : '' });
      },
      error: () => this.error.set('No pudimos cargar ese borrador.')
    });
  }

  // ---------- validación por paso
  invalido(campo: string): boolean {
    const c = this.form.get(campo);
    if (!c || !this.intentado()) return false;
    if (campo === 'variedadSel' && this.v().variedadSel === OTRA) return !this.variedad();
    return c.invalid;
  }

  private pasoValido(): boolean {
    const f = this.form.controls;
    const p = this.paso();
    if (p === 1) {
      const sinVariedad = !this.variedad();
      return f.producto.valid && !sinVariedad && f.cantidad.valid && f.unidad.valid && f.fecha_cosecha.valid && f.finca.valid;
    }
    if (p === 2) return f.finca.valid;
    return !!f.confirmo.value;
  }

  // ---------- guardado
  private payload() {
    const x = this.form.getRawValue();
    return {
      producto: Number(x.producto), finca: Number(x.finca), variedad: this.variedad(),
      cantidad: Number(x.cantidad) || 0, unidad: x.unidad, fecha_cosecha: x.fecha_cosecha,
      proceso: x.proceso ?? '', notas_produccion: x.notas_produccion ?? '',
    };
  }

  /** Crea o actualiza el borrador. Devuelve el id vía callback. */
  private guardar(alTerminar: (id: number) => void) {
    this.guardando.set(true); this.error.set('');
    const id = this.loteId();
    const peticion = id ? this.api.actualizarLote(id, this.payload()) : this.api.crearLote(this.payload());
    peticion.subscribe({
      next: l => { this.loteId.set(l.id); this.guardando.set(false); alTerminar(l.id); },
      error: err => {
        this.guardando.set(false);
        const d = err?.error ?? {};
        this.error.set(d.finca?.[0] ?? d.fecha_cosecha?.[0] ?? d.cantidad?.[0] ?? d.detail ?? 'No pudimos guardar el lote. Revisa los datos e inténtalo de nuevo.');
      }
    });
  }

  guardarBorrador() {
    const f = this.form.controls;
    if (f.producto.invalid || f.finca.invalid || f.fecha_cosecha.invalid) {
      this.intentado.set(true);
      this.error.set('Para guardar el borrador elige al menos el producto, la finca y la fecha de cosecha.');
      return;
    }
    this.guardar(() => {
      const h = new Date();
      this.mensaje.set(`Borrador guardado a las ${String(h.getHours()).padStart(2, '0')}:${String(h.getMinutes()).padStart(2, '0')}.`);
    });
  }

  continuar() {
    this.mensaje.set(''); this.error.set('');
    if (!this.pasoValido()) { this.intentado.set(true); return; }
    this.intentado.set(false);
    if (this.paso() === 3) { this.publicar(); return; }
    this.guardar(() => this.irA((this.paso() + 1) as 2 | 3));
  }

  private publicar() {
    this.guardar(id => {
      this.guardando.set(true);
      this.api.publicarLote(id).subscribe({
        next: r => { this.publicado.set(r); this.guardando.set(false); this.irA(4); },
        error: err => {
          this.guardando.set(false);
          this.error.set(err?.error?.error ?? 'No pudimos publicar el lote.');
        }
      });
    });
  }

  anterior() { this.mensaje.set(''); this.error.set(''); this.irA((this.paso() - 1) as 1 | 2); }
  irA(p: 1 | 2 | 3 | 4) { this.paso.set(p); window.scrollTo({ top: 0 }); }
  cancelar() { this.router.navigate(['/dashboard/resumen']); }

  registrarOtro() {
    this.form.reset({ unidad: 'kg', confirmo: false });
    if (this.fincas().length === 1) this.form.patchValue({ finca: String(this.fincas()[0].id) });
    this.loteId.set(null); this.publicado.set(null); this.mensaje.set(''); this.intentado.set(false);
    this.irA(1);
  }

  // ---------- paso 4
  enlace = computed(() => this.publicado()?.qr_codigo ?? '');
  copiarEnlace() {
    navigator.clipboard?.writeText(this.enlace()).then(() => {
      this.copiado.set(true); setTimeout(() => this.copiado.set(false), 2000);
    });
  }
  /** "Descargar etiqueta PDF": abre el diálogo de impresión solo con la etiqueta (Guardar como PDF). */
  imprimirEtiqueta() {
    document.body.classList.add('imprimiendo-etiqueta');
    window.print();
    document.body.classList.remove('imprimiendo-etiqueta');
  }

  // ---------- formato
  estadoPaso(n: number): 'hecho' | 'actual' | 'pendiente' {
    const p = this.paso();
    return n < p || p === 4 ? 'hecho' : n === p ? 'actual' : 'pendiente';
  }
  fecha(iso: string) {
    if (!iso) return 'Por definir';
    const [a, m, d] = iso.split('-').map(Number);
    return `${String(d).padStart(2, '0')} ${MESES[m - 1]} ${a}`;
  }
  private coord(valor: string | null | undefined, pos: string, neg: string) {
    if (valor === null || valor === undefined || valor === '') return 'No registrada';
    const n = Number(valor);
    return `${Math.abs(n).toFixed(4)}° ${n >= 0 ? pos : neg}`;
  }
  minusculas(t: string) { return (t ?? '').toLowerCase(); }
  nombreCorto(n: string) { return (n ?? '').replace(/^Finca\s+/i, ''); }
}
