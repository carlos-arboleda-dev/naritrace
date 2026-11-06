import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CrearFinca } from './crear-finca';

describe('CrearFinca', () => {
  let component: CrearFinca;
  let fixture: ComponentFixture<CrearFinca>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrearFinca],
    }).compileComponents();

    fixture = TestBed.createComponent(CrearFinca);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
